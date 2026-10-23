"""Separate annual Earth mobilization from conserved project transfers."""
from simulation.offworld_mvp.build8.three_arm_stage1.multi_project_campaign_kt_20261022 import run_multi_project as m
from simulation.offworld_mvp.build8.three_arm_stage1.general_project_v2_kt_20261022.general_project import _total_money

class BoundaryAwareCampaign(m.PortfolioCampaign):
    def on_year(self, year, kernel, rows):
        # Route 1 creates funded EARTH_BOUNDARY origin accounts before on_year.
        # Its annual injection is an explicit external boundary condition.
        # Project actions within this callback must still conserve exactly.
        self.initial_total = _total_money(kernel)
        super().on_year(year, kernel, rows)

m.PortfolioCampaign = BoundaryAwareCampaign
if __name__ == '__main__':
    m.main()
