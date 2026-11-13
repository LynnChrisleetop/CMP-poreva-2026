#!/usr/bin/env python3
"""CPU-only, auditable target/coordinate preparation; never repairs a structure.

python prepare_target.py --config project/configs/target_inputs/TARGET.json --out DIR
python prepare_target.py --self-test

Requires Python >=3.10 and Biopython. Relative input paths are resolved against
the config file, and retained as relative paths in the manifest. The manifest
does not include its own hash. Inputs are never overwritten.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import sys
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import Bio
from Bio import Align, SeqIO
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.PDB.mmcifio import MMCIFIO
from Bio.PDB.Polypeptide import protein_letters_3to1_extended

VERSION = '1.0.0'
AA = set('ACDEFGHIKLMNPQRSTVWY')
EMPTY = {'', '.', '?'}
GLYCANS = {'NAG', 'NDG', 'BMA', 'MAN', 'FUC', 'FUL', 'GAL', 'GLC', 'SIA', 'NAN', 'NEU', 'BGC'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def array(d, key):
    value = d.get(key, [])
    return value if isinstance(value, list) else [value]


def rows(d, prefix):
    keys = [key for key in d if key.startswith(prefix + '.')]
    if not keys:
        return []
    columns = {key.split('.', 1)[1]: array(d, key) for key in keys}
    n = max(map(len, columns.values()))
    if any(len(values) != n for values in columns.values()):
        raise ValueError('Inconsistent mmCIF category column lengths: ' + prefix)
    return [{key: value[i] for key, value in columns.items()} for i in range(n)]


def val(row, key, default=''):
    value = str(row.get(key, default))
    return default if value in EMPTY else value


def one_letter(mon):
    return protein_letters_3to1_extended.get(mon.upper(), 'X')


def canonical_polymer_sequence(text):
    text = re.sub(r'\(([^)]+)\)', lambda m: one_letter(m.group(1)), text)
    return re.sub(r'\s', '', text).upper()


def write_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_tsv(path, records, columns):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, delimiter='\t', lineterminator='\n', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(records)


def alignment_mapping(canonical, entity):
    """Whole-reference semiglobal mapping; ends are free, internal gaps penalized.

    Maps zero-based canonical indices to zero-based entity indices. Residues are
    never concatenated after removing missing internal residues. Mapping is an
    alignment inference, not a SIFTS claim. Equal-score alternatives are flagged.
    """
    aligner = Align.PairwiseAligner()
    aligner.mode = 'global'
    aligner.match_score = 3
    aligner.mismatch_score = -3
    aligner.open_gap_score = -8
    aligner.extend_gap_score = -0.5
    aligner.left_insertion_score = 0
    aligner.right_insertion_score = 0
    aligner.left_deletion_score = 0
    aligner.right_deletion_score = 0
    alignments = aligner.align(canonical, entity)
    first = alignments[0]

    def mapping_of(alignment):
        mapping = {}
        for (a, b), (c, d) in zip(*alignment.aligned):
            if b - a != d - c:
                raise ValueError('Unexpected non-diagonal aligned block')
            mapping.update((int(a + k), int(c + k)) for k in range(int(b - a)))
        return mapping

    mapping = mapping_of(first)
    try:
        alternative = alignments[1]
        ambiguous = mapping_of(alternative) != mapping
        alternative_exists = True
    except IndexError:
        ambiguous = False
        alternative_exists = False
    n = len(mapping)
    exact = sum(canonical[i] == entity[j] and canonical[i] != 'X' for i, j in mapping.items())
    return mapping, {'score': float(first.score), 'aligned_pairs': n,
                     'identity_over_aligned_pairs': exact / n if n else 0.0,
                     'equal_score_alternative_mapping': ambiguous,
                     'equal_score_alternative_alignment_exists': alternative_exists,
                     'algorithm': 'Biopython PairwiseAligner semiglobal; match=3 mismatch=-3 open=-8 extend=-0.5; both terminal gaps=0'}


def read_target(config, base):
    fasta_path = (base / config['target_fasta']).resolve()
    records = list(SeqIO.parse(str(fasta_path), 'fasta'))
    if len(records) != 1:
        raise ValueError('Target FASTA must contain exactly one record')
    sequence = str(records[0].seq).upper()
    if not sequence or not set(sequence) <= AA:
        raise ValueError('Target must contain only the 20 standard amino acids')
    uniprot_path = (base / config['uniprot_json']).resolve()
    uniprot = json.loads(uniprot_path.read_text(encoding='utf-8'))
    canonical = uniprot['sequence']['value'].upper()
    start, end = int(config['target_start']), int(config['target_end'])
    if not (1 <= start <= end <= len(canonical)):
        raise ValueError('Target bounds are outside the canonical UniProt sequence')
    if end - start + 1 != len(sequence):
        raise ValueError('Target FASTA length does not equal canonical interval length')
    accession_parts = config['accession'].split('-')
    if len(accession_parts) > 1 and accession_parts[1] != '1':
        raise ValueError('Non-canonical isoform requires an explicit isoform reference; this tool only accepts canonical or -1 accession')
    accession = accession_parts[0]
    if accession != uniprot['primaryAccession'] and accession not in uniprot.get('secondaryAccessions', []):
        raise ValueError('UniProt record does not match configured accession')
    substitutions = [{'target_index': i + 1, 'uniprot_index': start + i, 'target_aa': a, 'uniprot_aa': b}
                     for i, (a, b) in enumerate(zip(sequence, canonical[start - 1:end])) if a != b]
    if substitutions and not config.get('allow_target_substitutions', False):
        raise ValueError('Official target FASTA differs from the requested canonical slice; refusing silent correction: ' + json.dumps(substitutions))
    features = []
    for feature in uniprot.get('features', []):
        loc = feature.get('location', {})
        a, b = loc.get('start', {}).get('value'), loc.get('end', {}).get('value')
        if a is None or b is None or b < start or a > end:
            continue
        if feature.get('type') in {'Glycosylation', 'Disulfide bond', 'Signal', 'Transit peptide', 'Transmembrane', 'Topological domain', 'Chain', 'Propeptide'}:
            features.append(feature)
    motifs = [{'target_index': i + 1, 'uniprot_index': start + i, 'motif': sequence[i:i + 3],
               'meaning': 'Sequence sequon only; not proof of glycan occupancy'}
              for i in range(len(sequence) - 2) if sequence[i] == 'N' and sequence[i + 1] != 'P' and sequence[i + 2] in 'ST']
    evidence = {'accession': config['accession'], 'primary_accession': uniprot['primaryAccession'],
                'organism': uniprot.get('organism'), 'target_fasta_record': records[0].description,
                'target_interval_1_based_inclusive': [start, end], 'target_length': len(sequence),
                'canonical_length': len(canonical), 'exact_canonical_slice_match': not substitutions,
                'target_substitutions': substitutions, 'overlapping_uniprot_features': features,
                'n_linked_sequons': motifs,
                'warning': 'Feature evidence is retained from UniProt; sequons and annotations do not establish occupancy in the competition reagent.'}
    return sequence, canonical, start, end, evidence


def load_structure(cif_path):
    d = MMCIF2Dict(str(cif_path))
    atoms = rows(d, '_atom_site')
    if not atoms:
        raise ValueError('No coordinate atoms in mmCIF')
    model = val(atoms[0], 'pdbx_PDB_model_num', '1')
    atoms = [a for a in atoms if val(a, 'pdbx_PDB_model_num', '1') == model]
    chains = {str(r['id']): str(r['entity_id']) for r in rows(d, '_struct_asym')}
    entity_records = {str(r['entity_id']): r for r in rows(d, '_entity_poly')}
    entity_sequences = {}
    entity_sources = {}
    for key, row in entity_records.items():
        if 'polypeptide' not in row.get('type', ''):
            continue
        sequence = canonical_polymer_sequence(row.get('pdbx_seq_one_letter_code_can', row.get('pdbx_seq_one_letter_code', '')))
        if sequence:
            entity_sequences[key] = sequence
            entity_sources[key] = 'deposited_entity_poly_sequence'
    for atom in atoms:
        chain = val(atom, 'label_asym_id')
        entity = val(atom, 'label_entity_id', chain)
        chains.setdefault(chain, entity)
    atom_residues = defaultdict(list)
    for atom in atoms:
        labelseq = val(atom, 'label_seq_id')
        if not labelseq or not labelseq.lstrip('-').isdigit():
            continue
        atom_residues[(atom['label_asym_id'], int(labelseq))].append(atom)
    # AFDB/coordinate-only fallback. Unknown internal label positions remain X.
    # Never infer a full declared sequence merely by concatenating observed atoms.
    for chain, entity in list(chains.items()):
        if entity in entity_sequences:
            continue
        positions = {pos: one_letter(aa[0].get('label_comp_id', 'UNK')) for (ch, pos), aa in atom_residues.items() if ch == chain}
        if not positions:
            continue
        if min(positions) < 1 or max(positions) > 20000:
            raise ValueError('Unsupported atom-derived label_seq_id range for ' + chain)
        pseudo = 'atomderived_' + chain
        chains[chain] = pseudo
        entity_sequences[pseudo] = ''.join(positions.get(pos, 'X') for pos in range(1, max(positions) + 1))
        entity_sources[pseudo] = 'atom_site_derived; missing label_seq_id positions represented as X; no full polymer sequence declaration'
    scheme = defaultdict(list)
    for row in rows(d, '_pdbx_poly_seq_scheme'):
        seqid = val(row, 'seq_id')
        if seqid.lstrip('-').isdigit():
            scheme[(row['asym_id'], int(seqid))].append(row)
    return d, atoms, model, chains, entity_sequences, entity_sources, atom_residues, scheme


MAP_FIELDS = ['structure_id', 'label_chain', 'auth_chain', 'entity_id', 'target_index', 'uniprot_index',
              'target_aa', 'canonical_aa', 'label_seq_id', 'auth_seq_id', 'insertion_code',
              'scheme_pdb_seq_num', 'scheme_auth_seq_num', 'entity_aa', 'structure_aa',
              'has_coords', 'has_CA', 'backbone_N_CA_C_O_complete', 'match_status', 'numbering_basis']


def export_subset(d, atoms, selected, output, source_id):
    indices = []
    atom_rows = rows(d, '_atom_site')
    chosen_keys = {(a.get('id'), a.get('pdbx_PDB_model_num', '1')) for a in atoms if (a.get('label_asym_id'), val(a, 'label_seq_id')) in selected}
    for i, atom in enumerate(atom_rows):
        if (atom.get('id'), atom.get('pdbx_PDB_model_num', '1')) in chosen_keys:
            indices.append(i)
    if not indices:
        return 0
    subset = {'data_': re.sub(r'[^A-Za-z0-9_]', '_', source_id + '_target_observed'),
              '_entry.id': [source_id + '_target_observed'],
              '_struct.title': ['Observed target atoms only; no reconstruction, mutation repair, relaxation, or glycan completion.']}
    for key in d:
        if key.startswith('_atom_site.'):
            values = array(d, key)
            subset[key] = [values[i] for i in indices]
    writer = MMCIFIO()
    writer.set_dict(subset)
    writer.save(str(output))
    return len(indices)


def inspect_structure(spec, config, base, output, target, canonical, start, end):
    sid = spec['id']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', sid):
        raise ValueError('Structure id must be a safe filename token')
    cif_path = (base / spec['cif']).resolve()
    d, atoms, model, chains, entity_seqs, entity_sources, atom_residues, scheme = load_structure(cif_path)
    min_identity = float(spec.get('minimum_identity', 0.75))
    minimum_target_aligned = min(len(target), int(spec.get('minimum_target_aligned_residues', 20)))
    alignment_cache = {}
    contexts, accepted, maps, selected = [], [], [], set()
    preferred = spec.get('preferred_auth_chains', [])
    warnings = []
    glycan_comp_ids = {r.get('id', '') for r in rows(d, '_chem_comp') if 'saccharide' in r.get('type', '').lower()} | GLYCANS
    nonpoly = Counter()
    for atom in atoms:
        if val(atom, 'label_seq_id') == '':
            nonpoly[(atom.get('label_asym_id', ''), atom.get('auth_asym_id', ''), atom.get('label_comp_id', ''), val(atom, 'auth_seq_id'), val(atom, 'pdbx_PDB_ins_code'))] += 1
    for chain, entity in chains.items():
        seq = entity_seqs.get(entity)
        chain_atoms = [a for a in atoms if a.get('label_asym_id') == chain]
        auths = sorted({a.get('auth_asym_id', chain) for a in chain_atoms})
        if not auths:
            auths = sorted({val(r, 'pdb_strand_id', chain) for (ch, pos), rr in scheme.items() if ch == chain for r in rr})
        auth_chain = ','.join(auths) or chain
        if not seq:
            contexts.append({'label_chain': chain, 'auth_chains': auths, 'entity_id': entity, 'classification': 'non_target_or_non_polypeptide'})
            continue
        if entity not in alignment_cache:
            alignment_cache[entity] = alignment_mapping(canonical, seq)
        raw_mapping, raw_metrics = alignment_cache[entity]
        # Explicit reviewer-supplied entity positions exclude expression tags or
        # other reference artifacts. Deposited seq_dif numbering is retained for
        # review rather than guessed to be label_seq_id.
        configured_exclusions = spec.get('exclude_label_seq_ids', {})
        if isinstance(configured_exclusions, list):
            excluded = {int(i) for i in configured_exclusions}
        else:
            excluded = {int(i) for i in configured_exclusions.get('*', [])} | {int(i) for i in configured_exclusions.get(chain, [])}
        mapping = {i: j for i, j in raw_mapping.items() if j + 1 not in excluded}
        metrics = dict(raw_metrics)
        metrics['excluded_label_seq_ids'] = sorted(excluded)
        metrics['aligned_pairs_after_exclusions'] = len(mapping)
        metrics['identity_over_aligned_pairs_after_exclusions'] = (sum(canonical[i] == seq[j] and seq[j] != 'X' for i, j in mapping.items()) / len(mapping)) if mapping else 0.0
        mapped_target = {i: mapping[i] for i in range(start - 1, end) if i in mapping}
        aligned_count = len(mapped_target)
        target_identity = sum(target[i - start + 1] == seq[j] and seq[j] != 'X' for i, j in mapped_target.items()) / aligned_count if aligned_count else 0.0
        is_target = metrics['identity_over_aligned_pairs_after_exclusions'] >= min_identity and aligned_count >= minimum_target_aligned and target_identity >= min_identity
        context = {'label_chain': chain, 'auth_chains': auths, 'entity_id': entity,
                   'entity_length': len(seq), 'entity_sequence_source': entity_sources[entity],
                   'alignment': metrics, 'target_aligned_residues': aligned_count,
                   'target_identity_over_aligned_pairs': target_identity,
                   'classification': 'sequence_matched_target' if is_target else 'not_accepted_as_target'}
        contexts.append(context)
        if not is_target:
            continue
        chain_maps = []
        for index, aa in enumerate(target, 1):
            uniprot_index = start + index - 1
            canonical_index = uniprot_index - 1
            entity_index = mapping.get(canonical_index)
            row = dict.fromkeys(MAP_FIELDS, '')
            row.update(structure_id=sid, label_chain=chain, auth_chain=auth_chain, entity_id=entity,
                       target_index=index, uniprot_index=uniprot_index, target_aa=aa,
                       canonical_aa=canonical[canonical_index], has_coords=0, has_CA=0,
                       backbone_N_CA_C_O_complete=0, match_status='not_mapped_to_accepted_polymer_sequence')
            if entity_index is not None:
                labelseq = entity_index + 1
                row.update(label_seq_id=labelseq, entity_aa=seq[entity_index])
                schemerows = scheme.get((chain, labelseq), [])
                sch = schemerows[0] if schemerows else {}
                row['scheme_pdb_seq_num'] = val(sch, 'pdb_seq_num')
                row['scheme_auth_seq_num'] = val(sch, 'auth_seq_num')
                observed = atom_residues.get((chain, labelseq), [])
                row['match_status'] = 'sequence_match_without_coordinates' if aa == seq[entity_index] else 'sequence_mismatch_without_coordinates'
                if observed:
                    authnums = sorted({val(a, 'auth_seq_id') for a in observed})
                    incodes = sorted({val(a, 'pdbx_PDB_ins_code') for a in observed})
                    monomers = sorted({a.get('label_comp_id', 'UNK') for a in observed})
                    row.update(auth_seq_id=','.join(authnums), insertion_code=','.join(incodes),
                               structure_aa='/'.join(sorted({one_letter(m) for m in monomers})),
                               has_coords=1, numbering_basis='atom_site')
                    atomnames = {a.get('label_atom_id', a.get('auth_atom_id', '')) for a in observed}
                    row['has_CA'] = int('CA' in atomnames)
                    shared_atoms = {a.get('label_atom_id', a.get('auth_atom_id', '')) for a in observed if val(a, 'label_alt_id') == ''}
                    conformers = {val(a, 'label_alt_id') for a in observed} or {''}
                    compatible_atom_sets = [shared_atoms | {a.get('label_atom_id', a.get('auth_atom_id', '')) for a in observed if val(a, 'label_alt_id') == alt} for alt in conformers]
                    row['backbone_N_CA_C_O_complete'] = int(any({'N', 'CA', 'C', 'O'} <= names for names in compatible_atom_sets))
                    row['match_status'] = 'observed_match' if row['structure_aa'] == aa else 'observed_mismatch_or_microheterogeneity'
                    if len(authnums) > 1 or len(incodes) > 1 or len(monomers) > 1:
                        row['match_status'] = 'observed_ambiguous_numbering_or_microheterogeneity'
                    selected.add((chain, str(labelseq)))
                else:
                    row['auth_seq_id'] = val(sch, 'auth_seq_num', val(sch, 'pdb_seq_num'))
                    row['insertion_code'] = val(sch, 'pdb_ins_code')
                    row['numbering_basis'] = 'poly_seq_scheme_only; no observed atom' if sch else 'no_author_number_available'
            chain_maps.append(row)
        maps.extend(chain_maps)
        summary = dict(context)
        summary.update(target_length=len(target), mapped_sequence_residues=aligned_count,
                       observed_residues=sum(int(r['has_coords']) for r in chain_maps),
                       observed_CA_residues=sum(int(r['has_CA']) for r in chain_maps),
                       complete_backbone_residues=sum(int(r['backbone_N_CA_C_O_complete']) for r in chain_maps),
                       sequence_mismatch_residues=[int(r['target_index']) for r in chain_maps if r['entity_aa'] and r['entity_aa'] != r['target_aa']],
                       coordinate_mismatch_residues=[int(r['target_index']) for r in chain_maps if r['has_coords'] and r['structure_aa'] != r['target_aa']],
                       not_in_polymer_residues=[int(r['target_index']) for r in chain_maps if not r['label_seq_id']],
                       mapped_without_coordinates=[int(r['target_index']) for r in chain_maps if r['label_seq_id'] and not r['has_coords']],
                       preferred_auth_chain_match=bool(set(auths) & set(preferred)) if preferred else None)
        summary['observed_CA_fraction'] = summary['observed_CA_residues'] / len(target)
        accepted.append(summary)
    if not accepted:
        warnings.append('No sequence-matched target polymer chain passed the acceptance criteria; no prepared coordinates emitted.')
    if preferred and not any(c['preferred_auth_chain_match'] for c in accepted):
        warnings.append('Requested author-chain hint did not match an accepted target chain; inspect actual label/auth chain table.')
    if any(c['alignment']['equal_score_alternative_alignment_exists'] for c in accepted):
        warnings.append('At least one sequence alignment has an equal-score alternative; mapping requires manual review before use.')
    if any(c['entity_sequence_source'].startswith('atom_site_derived') for c in accepted):
        warnings.append('At least one chain uses atom-derived sequence fallback; missing terminal or internal residues cannot be established from a deposited full polymer sequence.')
    if any(c['sequence_mismatch_residues'] or c['coordinate_mismatch_residues'] for c in accepted):
        warnings.append('Reference has substitutions or microheterogeneity relative to the official target; coordinates have NOT been corrected.')
    if any(c['observed_CA_residues'] < len(target) for c in accepted):
        warnings.append('Coordinates do not cover the entire official target; missing regions have NOT been reconstructed.')
    glycan_rows = [{'label_chain': k[0], 'auth_chain': k[1], 'component': k[2], 'auth_seq_id': k[3], 'insertion_code': k[4], 'atoms': count}
                   for k, count in nonpoly.items() if k[2] in glycan_comp_ids]
    if glycan_rows:
        warnings.append('Deposited glycan coordinates exist in raw context and are omitted from the target-only subset; review steric accessibility against raw context.')
    # Always retain original partner/ligand/assembly evidence; do not infer assemblies.
    summary = {'structure_id': sid, 'input_cif': spec['cif'], 'source_kind': spec.get('source_kind', 'unspecified'),
               'role': spec.get('role', 'reference'), 'selected_model': model,
               'target_chain_acceptance': {'minimum_identity': min_identity, 'minimum_target_aligned_residues': minimum_target_aligned,
                                           'mapping_basis': 'Sequence alignment inference; not SIFTS residue mapping'},
               'preferred_auth_chains': preferred, 'polymer_and_chain_context': contexts, 'accepted_target_chains': accepted,
               'nonpolymer_coordinate_residues': [{'label_chain': k[0], 'auth_chain': k[1], 'component': k[2], 'auth_seq_id': k[3], 'insertion_code': k[4], 'atoms': count} for k, count in nonpoly.items()],
               'observed_glycan_residues': glycan_rows,
               'deposited_crossreferences': rows(d, '_struct_ref'),
               'deposited_reference_alignment': rows(d, '_struct_ref_seq'),
               'deposited_sequence_differences': rows(d, '_struct_ref_seq_dif'),
               'reviewer_supplied_excluded_label_seq_ids': spec.get('exclude_label_seq_ids', {}),
               'assemblies': rows(d, '_pdbx_struct_assembly'),
               'assembly_generators': rows(d, '_pdbx_struct_assembly_gen'),
               'assembly_operators': rows(d, '_pdbx_struct_oper_list'),
               'connections': rows(d, '_struct_conn'),
               'warnings': warnings, 'assembly_transforms_applied_by_this_tool': False,
               'prepared_coordinate_policy': 'Only observed atoms of accepted target chains within mapped official-target positions; original label/auth residue and chain IDs, insertion codes, model and altlocs retained. Coordinate-only mmCIF; full polymer sequence and partner/glycan context remain in raw source. No repair, minimization, protonation, mutation correction, or glycan completion.'}
    mapping_name = sid + '.residue_map.tsv'
    write_tsv(output / mapping_name, maps, MAP_FIELDS)
    summary['mapping_file'] = mapping_name
    summary['mapping_row_count'] = len(maps)
    assert len(maps) == len(target) * len(accepted), 'Residue-map row count mismatch'
    coords_name = sid + '.target_observed.cif'
    selected_atom_count = export_subset(d, atoms, selected, output / coords_name, sid)
    summary['prepared_coordinate_file'] = coords_name if selected_atom_count else None
    summary['prepared_atom_count'] = selected_atom_count
    summary['status'] = 'reference_rejected' if not accepted else 'coordinates_and_mapping_ready_for_review'
    write_json(output / (sid + '.summary.json'), summary)
    return summary


def prepare(config_path, output):
    config_path = Path(config_path).resolve()
    base = config_path.parent
    config = json.loads(config_path.read_text(encoding='utf-8'))
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty to avoid stale or overwritten artifacts')
    output.mkdir(parents=True, exist_ok=True)
    target, canonical, start, end, sequence_evidence = read_target(config, base)
    write_json(output / 'sequence_review.json', sequence_evidence)
    structures = []
    for original in config.get('structures', []):
        spec = dict(original)
        structures.append(spec)
        if spec.get('assembly_cif'):
            assembly = {**spec, 'id': spec['id'] + '_assembly', 'cif': spec['assembly_cif'],
                        'role': spec.get('assembly_role', 'downloaded biological assembly; verify metadata'),
                        'assembly_cif': None}
            structures.append(assembly)
    summaries = []
    for spec in structures:
        summaries.append(inspect_structure(spec, config, base, output, target, canonical, start, end))
    lines = ['# 靶点结构输入包审查', '',
             f"目标：{config['target_id']}；比赛：{config['competition']}；物种：{config['species']}。", '',
             f"官方序列：{len(target)} aa；UniProt：{config['accession']}，1-based闭区间 {start}–{end}。", '',
             f"官方序列与UniProt指定切片完全一致：{'是' if sequence_evidence['exact_canonical_slice_match'] else '否，已显式记录差异'}。", '',
             '## 如何使用', '',
             '- `sequence_review.json` 保留序列校验、UniProt功能区注释和N-X-S/T序列位点。序列位点不等于糖链占位。',
             '- `*.residue_map.tsv` 对每条接受的目标链逐一列出所有官方目标残基，包括没有坐标的残基。编号不连续与插入码均保留。',
             '- `*.target_observed.cif` 只包含已观测到的目标原子。没有补齐缺口、修复突变、添加糖链或优化结构；必须结合原始完整结构审查。',
             '- `*.summary.json` 记录链筛选、覆盖率、变异、糖链、其它分子、装配操作和警告。工具不自行把非对称单元扩展成生物学装配。',
             '- 映射由全长参考序列与沉积聚合物序列比对推断，并非SIFTS映射。预测结构必须按预测证据使用。', '',
             '## 结构检查结果', '',
             '| 结构 | 证据类型 | 目标链（label/auth） | 有CA坐标/官方长度 | 序列差异位点数 |', '|---|---|---|---:|---:|']
    for summary in summaries:
        for chain in summary['accepted_target_chains']:
            lines.append(f"| {summary['structure_id']} | {summary['source_kind']} | {chain['label_chain']}/{'、'.join(chain['auth_chains'])} | {chain['observed_CA_residues']}/{len(target)} | {len(chain['sequence_mismatch_residues'])} |")
        if not summary['accepted_target_chains']:
            lines.append(f"| {summary['structure_id']} | {summary['source_kind']} | 无通过链 | 0/{len(target)} | 不适用 |")
    lines += ['', '## 仍需审查', '']
    for summary in summaries:
        for warning in summary['warnings']:
            lines.append(f"- **{summary['structure_id']}**：{warning}")
    lines += ['', '上述文件是来源明确的参考输入与映射，不代表已经验证结合、表达、pH行为或功能，也不表示完整模型输入已满足某个特定设计软件的要求。', '']
    (output / 'README.md').write_text('\n'.join(lines), encoding='utf-8')
    paths = [('target_fasta', config['target_fasta']), ('uniprot_json', config['uniprot_json'])]
    paths += [('structure_cif', spec['cif']) for spec in structures]
    inputs = [{'role': role, 'path_relative_to_config': rel, 'sha256': digest(base / rel), 'bytes': (base / rel).stat().st_size} for role, rel in paths]
    outputs = [{'path_relative_to_output': path.name, 'bytes': path.stat().st_size, 'sha256': digest(path)} for path in sorted(output.iterdir()) if path.is_file()]
    manifest = {'schema_version': 1, 'tool': {'name': 'prepare_target.py', 'version': VERSION, 'sha256': digest(__file__),
                                             'python': platform.python_version(), 'biopython': Bio.__version__},
                'created_at': datetime.now(timezone.utc).isoformat(), 'target_id': config['target_id'],
                'competition': config['competition'], 'species': config['species'],
                'config_filename': config_path.name, 'config_sha256': digest(config_path),
                'input_paths_relative_to': 'config directory', 'inputs': inputs, 'outputs': outputs,
                'sequence_exact_slice_match': sequence_evidence['exact_canonical_slice_match'],
                'structure_count': len(summaries), 'accepted_target_chain_count': sum(len(s['accepted_target_chains']) for s in summaries),
                'all_structures_have_a_target_chain': bool(summaries) and all(s['accepted_target_chains'] for s in summaries),
                'status': 'reference_pack_prepared_for_review',
                'limitations': ['No missing-coordinate reconstruction or sequence mutation repair', 'No GPU design, folding, or scoring',
                                'No experimental biological-function claim', 'Biological assembly transformations are not applied by this tool',
                                'Generated mmCIF is a coordinate-only target subset; keep raw complete source and residue_map.tsv together']}
    write_json(output / 'manifest.json', manifest)
    return manifest


def self_test():
    """Synthetic numbering, truncation, missing residue, substitution and multi-chain tests."""
    sequence = 'ACDEFGHIKLMNPQRSTVWY'
    truncated = sequence[2:-2]
    mapping, metrics = alignment_mapping(sequence, truncated)
    assert mapping[2] == 0 and mapping[17] == 15 and 0 not in mapping and 19 not in mapping
    assert metrics['identity_over_aligned_pairs'] == 1
    altered = truncated[:7] + 'A' + truncated[8:]
    mapping2, _ = alignment_mapping(sequence, altered)
    assert mapping2[9] == 7
    names = {v: k for k, v in protein_letters_3to1_extended.items() if k in {'ALA','CYS','ASP','GLU','PHE','GLY','HIS','ILE','LYS','LEU','MET','ASN','PRO','GLN','ARG','SER','THR','VAL','TRP','TYR'}}
    with tempfile.TemporaryDirectory(prefix='target-preparation-test-') as temp:
        base = Path(temp)
        cif = {'data_': 'synthetic', '_entity_poly.entity_id': ['1'], '_entity_poly.type': ['polypeptide(L)'],
               '_entity_poly.pdbx_seq_one_letter_code_can': [altered],
               '_struct_asym.id': ['A', 'B'], '_struct_asym.entity_id': ['1', '1']}
        atom_columns = ['group_PDB','id','type_symbol','label_atom_id','label_alt_id','label_comp_id','label_asym_id','label_entity_id','label_seq_id','pdbx_PDB_ins_code','Cartn_x','Cartn_y','Cartn_z','occupancy','B_iso_or_equiv','auth_seq_id','auth_comp_id','auth_asym_id','auth_atom_id','pdbx_PDB_model_num']
        atomvalues = {key: [] for key in atom_columns}
        schemevalues = {key: [] for key in ['asym_id','entity_id','seq_id','mon_id','pdb_seq_num','auth_seq_num','pdb_strand_id','pdb_ins_code']}
        serial = 1
        for chain in ['A', 'B']:
            for i, aa in enumerate(altered, 1):
                for key, value in zip(schemevalues, [chain, '1', str(i), names[aa], str(100 + i), str(100 + i), chain, 'A' if i == 5 else '.']):
                    schemevalues[key].append(value)
                if i == 6:
                    continue
                for atomname in ['N', 'CA', 'C', 'O']:
                    vals = ['ATOM', str(serial), atomname[0], atomname, '.', names[aa], chain, '1', str(i), 'A' if i == 5 else '.', str(i), '0','0','1','20',str(100+i),names[aa],chain,atomname,'1']
                    for key, value in zip(atom_columns, vals):
                        atomvalues[key].append(value)
                    serial += 1
        cif.update({'_atom_site.' + key: values for key, values in atomvalues.items()})
        cif.update({'_pdbx_poly_seq_scheme.' + key: values for key, values in schemevalues.items()})
        writer = MMCIFIO(); writer.set_dict(cif); writer.save(str(base / 'source.cif'))
        (base / 'target.fasta').write_text('>test\n' + sequence + '\n', encoding='utf-8')
        write_json(base / 'uniprot.json', {'primaryAccession': 'TEST', 'sequence': {'value': sequence}, 'features': []})
        config = {'target_id': 'TEST', 'competition': 'synthetic', 'species': 'test', 'accession': 'TEST', 'target_fasta': 'target.fasta', 'uniprot_json': 'uniprot.json', 'target_start': 1, 'target_end': 20,
                  'structures': [{'id': 'TEST', 'cif': 'source.cif', 'minimum_target_aligned_residues': 10, 'source_kind': 'synthetic'}]}
        write_json(base / 'config.json', config)
        prepare(base / 'config.json', base / 'out')
        summary = json.loads((base / 'out' / 'TEST.summary.json').read_text(encoding='utf-8'))
        assert len(summary['accepted_target_chains']) == 2
        assert summary['mapping_row_count'] == 40
        assert summary['prepared_atom_count'] == 120
        c = summary['accepted_target_chains'][0]
        assert c['observed_CA_residues'] == 15
        assert c['mapped_without_coordinates'] == [8]
        assert c['sequence_mismatch_residues'] == [10]
        assert c['not_in_polymer_residues'] == [1, 2, 19, 20]
        with (base / 'out' / 'TEST.residue_map.tsv').open(encoding='utf-8') as stream:
            rr = list(csv.DictReader(stream, delimiter='\t'))
        assert rr[6]['insertion_code'] == 'A' and rr[6]['auth_seq_id'] == '105'
        assert rr[7]['has_coords'] == '0' and rr[7]['auth_seq_id'] == '106'
        assert rr[9]['structure_aa'] == 'A' and rr[9]['target_aa'] == 'L'
        extracted = MMCIF2Dict(str(base / 'out' / 'TEST.target_observed.cif'))
        assert len(array(extracted, '_atom_site.id')) == 120
        # A coordinate-only / AFDB-style fallback retains unknown internal gaps
        # rather than concatenating residues and shifting all later mappings.
        fallback_config = {**config, 'structures': [{'id': 'FALLBACK', 'cif': 'out/TEST.target_observed.cif', 'minimum_target_aligned_residues': 10, 'source_kind': 'synthetic coordinate-only'}]}
        write_json(base / 'fallback.json', fallback_config)
        prepare(base / 'fallback.json', base / 'fallback-out')
        fallback = json.loads((base / 'fallback-out' / 'FALLBACK.summary.json').read_text(encoding='utf-8'))
        assert fallback['accepted_target_chains'][0]['observed_CA_residues'] == 15
        assert fallback['accepted_target_chains'][0]['mapped_without_coordinates'] == [8]
        assert fallback['accepted_target_chains'][0]['entity_sequence_source'].startswith('atom_site_derived')
        # Explicit artifact exclusion removes only reviewer-listed entity positions.
        excluded_config = {**config, 'structures': [{**config['structures'][0], 'exclude_label_seq_ids': {'A': [16]}}]}
        write_json(base / 'excluded.json', excluded_config)
        prepare(base / 'excluded.json', base / 'excluded-out')
        excluded = json.loads((base / 'excluded-out' / 'TEST.summary.json').read_text(encoding='utf-8'))
        assert excluded['accepted_target_chains'][0]['observed_CA_residues'] == 14
        assert excluded['accepted_target_chains'][1]['observed_CA_residues'] == 15
        # Reject a wrong-target chain without creating a coordinate file.
        config['structures'][0]['minimum_identity'] = 0.99
        write_json(base / 'strict.json', config)
        prepare(base / 'strict.json', base / 'strict-out')
        assert not (base / 'strict-out' / 'TEST.target_observed.cif').exists()
        # Canonical mismatch must be explicit, never silently repaired.
        (base / 'target.fasta').write_text('>wrong\nG' + sequence[1:] + '\n', encoding='utf-8')
        try:
            prepare(base / 'config.json', base / 'wrong-out')
        except ValueError as error:
            assert 'differs' in str(error)
        else:
            raise AssertionError('Expected canonical-slice mismatch to fail')
    print('PASS: semiglobal truncation, mutation, missing coordinates, insertion codes, duplicate target chains, target rejection, atom-subset roundtrip, canonical mismatch guard, coordinate-only fallback, explicit artifact exclusion')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config')
    parser.add_argument('--out')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.config and args.out:
        result = prepare(args.config, args.out)
        print(json.dumps({k: result[k] for k in ['target_id', 'structure_count', 'accepted_target_chain_count', 'sequence_exact_slice_match', 'status']}, ensure_ascii=False))
    else:
        parser.error('--config and --out are required unless --self-test is used')


if __name__ == '__main__':
    main()
