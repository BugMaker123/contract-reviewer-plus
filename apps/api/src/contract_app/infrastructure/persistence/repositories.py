from typing import Dict, List, Optional
import asyncio
from contract_app.modules.contracts.domain.contract import Contract
from contract_app.modules.documents.domain.version import DocumentVersion
from contract_app.modules.documents.domain.session import EditorSession
from contract_app.modules.reviews.domain.review_run import ReviewRun
from contract_app.modules.issues.domain.issue_group import IssueGroup
from contract_app.modules.revisions.domain.revision_plan import RevisionPlan
from contract_app.modules.revisions.domain.decision_command import DecisionCommand
from contract_app.modules.exports.domain.export_job import ExportJob
from contract_app.modules.checklists.domain.category import BusinessCategory
from contract_app.modules.checklists.domain.checklist_item import ChecklistItem

class RepositoryStore:
    def __init__(self):
        self.contracts: Dict[str, Contract] = {}
        self.versions: Dict[str, DocumentVersion] = {}
        self.sessions: Dict[str, EditorSession] = {}
        self.review_runs: Dict[str, ReviewRun] = {}
        self.issue_groups: Dict[str, List[IssueGroup]] = {}  # run_id -> list
        self.revision_plans: Dict[str, RevisionPlan] = {}   # plan_id -> plan
        self.decision_commands: Dict[str, DecisionCommand] = {}
        self.export_jobs: Dict[str, ExportJob] = {}
        self.categories: Dict[str, BusinessCategory] = {}
        self.checklists: Dict[str, ChecklistItem] = {}
        self._lock = asyncio.Lock()
        self._init_default_checklists()

    def _init_default_checklists(self):
        cat1 = BusinessCategory(id="cat_tech", name="技术开发与实施类", code="TECH_DEV", description="软硬件开发、技术外包及数据中台建设合同", sort_order=1)
        cat2 = BusinessCategory(id="cat_purchase", name="采购与供应链类", code="PURCHASE", description="设备采购、原料供应及仓储物流服务协议", sort_order=2)
        cat3 = BusinessCategory(id="cat_general", name="综合商务与合作类", code="BIZ_COOP", description="战略合作框架、渠道经销及商业委托协议", sort_order=3)
        for c in [cat1, cat2, cat3]:
            self.categories[c.id] = c

        chk_items = [
            ChecklistItem(
                id="chk_001",
                category_id=cat1.id,
                category_name=cat1.name,
                title="付款节点与验收先决条件明确",
                risk_level="high",
                standard_clause="款项分期支付须与阶段性验收报告绑定，尾款支付前须出具最终合格验收书及合规发票。",
                check_prompt="检查合同是否缺乏明确验收标准或付款与交付脱钩",
                prompt_template="请作为法务专家从【{stance}】立场核查条款【{clause_text}】是否满足付款先决条件原则。重点：款项支付须以书面合格验收凭据及全额合规发票为前提。若不满足，请指出货款失控风险并按照标准条款【{standard_clause}】生成替换建议。",
                sort_order=1
            ),
            ChecklistItem(
                id="chk_002",
                category_id=cat1.id,
                category_name=cat1.name,
                title="违约金责任上限与直接损失界定",
                risk_level="high",
                standard_clause="累计赔偿总额不得超过合同总金额的100%，明确排除间接损失、商业机会及预期利润损失。",
                check_prompt="检查是否有'无上限连带赔偿'或惩罚性超额违约金约定",
                prompt_template="请从【{stance}】立场审查条款【{clause_text}】中的违约赔偿责任。重点核查是否缺乏赔偿总额上限或未排除间接损失。若存在无限连带风险，请援引示范标准【{standard_clause}】输出限额修订表述。",
                sort_order=2
            ),
            ChecklistItem(
                id="chk_003",
                category_id=cat1.id,
                category_name=cat1.name,
                title="既有背景知识产权及衍生权属保留",
                risk_level="high",
                standard_clause="签约前各方拥有的背景知识产权仍归各自所有；交付物知识产权转让不包含通用底层工具。",
                check_prompt="审查是否存在无偿剥夺我方既有核心专利或源程序的侵权条款",
                prompt_template="请审查条款【{clause_text}】中的知识产权归属。严格确认签约前各方既有知识产权（Background IP）是否明确保留归各自所有。参考标准：【{standard_clause}】。",
                sort_order=3
            ),
            ChecklistItem(
                id="chk_004",
                category_id=cat2.id,
                category_name=cat2.name,
                title="交货迟延违约金比例合规（日千分之一至千分之三）",
                risk_level="medium",
                standard_clause="迟延交付违约金每日按逾期部分金额0.1%至0.3%计算，设置单项上限（如不超过标的额10%）。",
                check_prompt="核实逾期违约金是否超出法定利率标准或畸高",
                prompt_template="审查条款【{clause_text}】中迟延交货违约金约定。核查费率是否在每日0.1%~0.3%合理区间且设置累计上限（如不超过10%）。参考标准：【{standard_clause}】。",
                sort_order=4
            ),
            ChecklistItem(
                id="chk_005",
                category_id=cat3.id,
                category_name=cat3.name,
                title="单方解除权限制与催告宽限期保障（至少15日）",
                risk_level="high",
                standard_clause="任何一方主张违约解除合同，须先行书面通知并在给予不少于15个工作日补救宽限期后方可行使。",
                check_prompt="防范任意解除权及突击解约损害我方在途投入",
                prompt_template="审查条款【{clause_text}】中的解除权行使机制。重点防范任意无条件单方解约，必须保障至少15个工作日书面催告补救整改宽限期。参考标准：【{standard_clause}】。",
                sort_order=5
            ),
            ChecklistItem(
                id="chk_006",
                category_id=cat3.id,
                category_name=cat3.name,
                title="争议管辖法院优选我方/原告住所地人民法院",
                risk_level="low",
                standard_clause="发生争议协商不成的，向合同签订地或原告所在地有管辖权的人民法院提起诉讼。",
                check_prompt="防范不利异地管辖导致的维权差旅与诉讼成本风险",
                prompt_template="审查条款【{clause_text}】中的争议管辖法院。优选我方住所地或原告所在地人民法院，防范异地诉讼地方保护与维权成本。参考标准：【{standard_clause}】。",
                sort_order=6
            )
        ]
        for itm in chk_items:
            self.checklists[itm.id] = itm

    # Contracts
    async def save_contract(self, contract: Contract):
        async with self._lock:
            self.contracts[contract.id] = contract

    async def get_contract(self, contract_id: str) -> Optional[Contract]:
        return self.contracts.get(contract_id)

    async def delete_contract(self, contract_id: str) -> bool:
        async with self._lock:
            if contract_id in self.contracts:
                del self.contracts[contract_id]
                # cleanup versions and sessions
                ver_ids = [vid for vid, v in self.versions.items() if v.contract_id == contract_id]
                for vid in ver_ids:
                    del self.versions[vid]
                sess_ids = [sid for sid, s in self.sessions.items() if s.contract_id == contract_id]
                for sid in sess_ids:
                    del self.sessions[sid]
                return True
            return False

    async def list_contracts_paged(self, page: int = 1, page_size: int = 10, keyword: Optional[str] = None) -> tuple[List[Contract], int]:
        items = list(self.contracts.values())
        if keyword:
            kw = keyword.lower()
            items = [c for c in items if kw in c.title.lower() or kw in c.stance.lower()]
        items = sorted(items, key=lambda c: c.updated_at, reverse=True)
        total = len(items)
        start = (page - 1) * page_size
        return items[start:start + page_size], total

    async def list_contracts(self) -> List[Contract]:
        return sorted(list(self.contracts.values()), key=lambda c: c.updated_at, reverse=True)

    # Categories
    async def save_category(self, cat: BusinessCategory):
        async with self._lock:
            self.categories[cat.id] = cat

    async def get_category(self, cat_id: str) -> Optional[BusinessCategory]:
        return self.categories.get(cat_id)

    async def delete_category(self, cat_id: str) -> bool:
        async with self._lock:
            if cat_id in self.categories:
                del self.categories[cat_id]
                return True
            return False

    async def list_categories_paged(self, page: int = 1, page_size: int = 10, keyword: Optional[str] = None) -> tuple[List[BusinessCategory], int]:
        items = list(self.categories.values())
        if keyword:
            kw = keyword.lower()
            items = [c for c in items if kw in c.name.lower() or kw in c.code.lower()]
        items = sorted(items, key=lambda c: c.sort_order)
        total = len(items)
        start = (page - 1) * page_size
        return items[start:start + page_size], total

    async def list_all_categories(self) -> List[BusinessCategory]:
        return sorted(list(self.categories.values()), key=lambda c: c.sort_order)

    # Checklists
    async def save_checklist(self, item: ChecklistItem):
        async with self._lock:
            if item.category_id in self.categories:
                item.category_name = self.categories[item.category_id].name
            self.checklists[item.id] = item

    async def get_checklist(self, item_id: str) -> Optional[ChecklistItem]:
        return self.checklists.get(item_id)

    async def delete_checklist(self, item_id: str) -> bool:
        async with self._lock:
            if item_id in self.checklists:
                del self.checklists[item_id]
                return True
            return False

    async def list_checklists_paged(self, page: int = 1, page_size: int = 10, category_id: Optional[str] = None, keyword: Optional[str] = None) -> tuple[List[ChecklistItem], int]:
        items = list(self.checklists.values())
        if category_id:
            items = [i for i in items if i.category_id == category_id]
        if keyword:
            kw = keyword.lower()
            items = [i for i in items if kw in i.title.lower() or kw in (i.standard_clause or "").lower()]
        items = sorted(items, key=lambda i: i.sort_order)
        total = len(items)
        start = (page - 1) * page_size
        return items[start:start + page_size], total

    # Versions
    async def save_version(self, version: DocumentVersion):
        async with self._lock:
            self.versions[version.id] = version

    async def get_version(self, version_id: str) -> Optional[DocumentVersion]:
        return self.versions.get(version_id)

    async def list_versions_by_contract(self, contract_id: str) -> List[DocumentVersion]:
        res = [v for v in self.versions.values() if v.contract_id == contract_id]
        return sorted(res, key=lambda v: v.created_at, reverse=True)

    # Sessions
    async def save_session(self, session: EditorSession):
        async with self._lock:
            self.sessions[session.id] = session

    async def get_session(self, session_id: str) -> Optional[EditorSession]:
        return self.sessions.get(session_id)

    # Review Runs
    async def save_review_run(self, run: ReviewRun):
        async with self._lock:
            self.review_runs[run.id] = run

    async def get_review_run(self, run_id: str) -> Optional[ReviewRun]:
        return self.review_runs.get(run_id)

    # Issue Groups
    async def save_issue_groups(self, run_id: str, issues: List[IssueGroup]):
        async with self._lock:
            self.issue_groups[run_id] = issues

    async def get_issue_groups(self, run_id: str) -> List[IssueGroup]:
        return self.issue_groups.get(run_id, [])

    async def get_issue_group(self, run_id: str, issue_id: str) -> Optional[IssueGroup]:
        for ig in self.issue_groups.get(run_id, []):
            if ig.id == issue_id:
                return ig
        return None

    # Revision Plans
    async def save_revision_plan(self, plan: RevisionPlan):
        async with self._lock:
            self.revision_plans[plan.id] = plan

    async def get_revision_plan(self, plan_id: str) -> Optional[RevisionPlan]:
        return self.revision_plans.get(plan_id)

    # Decision Commands
    async def save_decision_command(self, cmd: DecisionCommand):
        async with self._lock:
            self.decision_commands[cmd.id] = cmd

    async def get_decision_command(self, cmd_id: str) -> Optional[DecisionCommand]:
        return self.decision_commands.get(cmd_id)

    # Export Jobs
    async def save_export_job(self, job: ExportJob):
        async with self._lock:
            self.export_jobs[job.id] = job

    async def get_export_job(self, job_id: str) -> Optional[ExportJob]:
        return self.export_jobs.get(job_id)

repo_store = RepositoryStore()
