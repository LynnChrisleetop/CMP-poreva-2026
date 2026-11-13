# pH 功能证据：TNFα 小试的判断边界

检索日期：2026-11-03。本文用于计算方案评审，不提供候选序列、残基改造配方或湿实验规程。TNFα 目标是 pH 7.4 结合、6.0 无可检测结合；EGFR 的方向相反，为6.5结合、7.4无可检测。计入60/200分的功能目标，应作为待测终点，而非可由计算分数直接兑换的结果。

## 1. 2025年论文确有 TNFα，但不是本题条件下的成功证明

《Computational design of pH-sensitive binders》不只研究 TNFR2。正文 Fig.3 的内部网络策略明确应用于一个**已有的 TNFα binder**：72个设计中48个保留结合，7个亲和力优于25 nM，其中3个具有pH敏感性；最佳设计在pH 5.4相对7.4的亲和力降低79倍。TNFR2属于另一组界面策略结果，不能混为同一靶点。[1]

这些结果支持“可在已有结合骨架上引入酸性释放行为”，但有三项外推限制。第一，5.4比本题6.0更酸，不能假设响应幅度不变。第二，亲和力降低79倍不等于低pH无可检测结合，是否检出还取决于绝对亲和力和检测窗口。第三，这是对已有binder的改造；48/72或3/72均不是未知起点完全从头设计的通用成功率。论文也没有为本次小批量设计提供经校准的成功概率。[1]

截至本次检索，所引用版本为2025-09-29的bioRxiv预印本，不能写成已完成同行评审的确定结论。参赛方案应研究其机制原则和证据组织方式；**不能拿发表的阳性序列当本项目起点**，应在我们自有的从头设计上研究方法原则，并保存来源与设计记录。

## 2. 更接近题目条件的实证及其限制

W1-Humira研究同时使用恒pH模拟、加速动力学和体外检测。其TNFα实验比较了7.4与6.0：改造抗体在7.4保留结合，6.0的ELISA信号接近零。这是同靶点、同pH方向的阳性先例，但抗体骨架、测量形式和检测下限不同；ELISA近零不能直接替代赛事结合动力学标准。该阳性抗体也不能复制为参赛设计。[2]

EGFR的G532提供相反方向的实证：人源EGFR的SPR测得KD在6.5为294 nM，在7.4为3.90 μM，差异约13.3倍。中性条件仍有可测结合，因此不能概括为“7.4关闭”。该例说明必须同时看两端绝对值，不能只报告倍数，更不能把抗体研究的表现直接移植到新骨架。[3]

## 3. 将计算结果按证据等级记录

- **结构可行性：**结构预测、界面置信度与几何检查支持折叠和接触方式的合理性。它们不直接测量pH依赖KD；高ipTM或低PAE不能证明酸性释放。
- **机制一致性：**预测pKa、比较合理质子化状态及相互作用，可检验是否存在解释目标方向的物理假设。应区分结合态与游离态，记录构象依赖和不确定性；单个残基pKa或一次静态能量差不足以决定整个分子的结合开关。
- **动态支持：**固定质子化MD只能比较事先指定状态，不会自行采样质子交换。恒pH MD允许质子化和构象耦合，但仍受力场、溶剂模型及采样收敛影响。原始GPU方法论文明确指出，埋藏或强相互作用位点可能需要更长的构象松弛。[4]
- **功能证据：**只有匹配目标pH与判定条件的数据，才支持“无可检测结合”。未测候选应标“未知”，不能写成计算已验证。短轨迹未解离不证明有真实亲和力，单次轨迹解离也不足以证明实验必然不结合。

PROPKA等静态工具适合产生和筛查质子化假设；不能把输出pKa直接转换为本题的开关阈值。对有限A100/L4预算，建议将较贵的恒pH分析用于少数候选的机制复核，报告重复间一致性和未收敛项，不以增加模拟时长替代功能验证。候选表分开列“结构支持、机制支持、动态支持、功能实测”，避免用一个综合分掩盖证据缺口。

## 4. 新工具仅列观察清单

2026年10月发布的Proton-PottsMPNN预印本提供模型、代码和权重，并有PD-L1酸性结合的酵母展示证据，主要展示5.0与7.4的比较。其状态能量差未标定为pKa或KD，酸性释放方向在文中仍属正在测试的扩展；固定骨架也限制了对构象切换的表达。因此，它可列入观察清单，不能充当TNFα 7.4/6.0小试的成熟主线或功能保证。[5]

## 原始来源

1. [Ahn et al. *Computational design of pH-sensitive binders*. bioRxiv，2025，预印本](https://pmc.ncbi.nlm.nih.gov/articles/PMC12621740/)
2. [*Anti-TNF Alpha Antibody Humira with pH-dependent Binding Characteristics: A constant-pH Molecular Dynamics, Gaussian Accelerated Molecular Dynamics, and In Vitro Study*. Biomolecules，2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC7926962/)
3. [*A cross-reactive pH-dependent EGFR antibody with improved tumor selectivity and penetration obtained by structure-guided engineering*. Molecular Therapy Oncolytics，2022](https://pmc.ncbi.nlm.nih.gov/articles/PMC9703009/)
4. [Harris and Shen. *GPU-Accelerated Implementation of Continuous Constant pH Molecular Dynamics in Amber: pKa Predictions with Single-pH Simulations*. Journal of Chemical Information and Modeling，2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6934042/)
5. [Jacobsen et al. *pH-sensitive binder design with Proton-PottsMPNN*. bioRxiv，2026，预印本；文末“Code and model availability”提供官方代码入口](https://www.biorxiv.org/content/10.64898/2026.09.30.755438v1.full)