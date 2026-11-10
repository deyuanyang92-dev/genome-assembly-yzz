# Type Genomics阅读来源与范围

论文：Letsch et al. 2025，*Type Genomics: A Framework for Integrating Genomic Data into Biodiversity and Taxonomic Research*，*Systematic Biology*74(6):1029–1044，[DOI10.1093/sysbio/syaf040](https://doi.org/10.1093/sysbio/syaf040)。中文归纳与本项目应用分析见[笔记64](../../64_Type_Genomics模式标本基因组与分类溯源.md)。

2026-11-05完成科学正文阅读（引言至Outlook）、图1–3逐图查看及补充表S1表体阅读。附件PDF共13页，表体第1–5页，参考文献始于第5页；额外渲染核对第2、4页表格。没有逐篇阅读所有引文，没有取得或逐页阅读主文PDF；没有实验或生物流程复现。ICZN Article72、73、75与Declaration45为相关条款定向核查，植物ICN未作独立系统核查。

| 文件 | 来源、用途与状态 |
|---|---|
| `article.xml` | Europe PMC全文XML；主文DOI与标题核对一致，保留原始字节 |
| `article_body.txt` | XML派生阅读文本，含摘要、引言及科学正文至Outlook；不含全部参考文献；原XML不变 |
| `supplementaryFiles.zip` | Europe PMC附件包；含图1–3及S1 PDF等，保留原包 |
| `syaf040fig1.jpg`至`syaf040fig3.jpg` | 原包中的作者原图；未改图 |
| `syaf040_supplemental_file.pdf` | 原包中的补充表S1，154490字节；与Dryad页面所列文件大小吻合，但未从Dryad直接取得文件，因此不宣称完成两站字节比较 |
| `supplement_S1.txt` | `pdftotext -layout`派生；有参考文献全文不代表引用文献已全部阅读 |
| `supplement_review_page02.png`、`supplement_review_page04.png` | `pdftoppm`渲染，供表格列对应复核；不是额外科学实验 |
| `pmc_browser_challenge.html` | 失败访问记录：curl取得的是浏览器验证页，**不是论文全文** |
| `review_ledger.json` | 文献身份、时间、阅读范围、文件SHA256、访问结果、命令、结论与边界 |
| `validation.json` | 来源/附件/文档链接与知识库索引检查；不表示生物学有效性验收 |

来源接口：

- [PMC主文](https://pmc.ncbi.nlm.nih.gov/articles/PMC12712332/)
- [Europe PMC全文XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12712332/fullTextXML)
- [Europe PMC附件包](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12712332/supplementaryFiles)
- [Dryad，10.5061/dryad.zs7h44jn5](https://datadryad.org/dataset/doi:10.5061/dryad.zs7h44jn5)，页面标注2025-07-08数据版本；直链下载本次403。

论文标注CC BY4.0，原文/原图归档注明Letsch等作者与DOI，中文笔记另标本项目推演。校验范围明确区分“读过”“来源文件可验证”“执行过文档处理命令”和“运行过生物学流程”。本批没有新增生物学实测、上游软件仓库或生产验收。
