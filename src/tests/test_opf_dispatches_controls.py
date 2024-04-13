# GridCal
# Copyright (C) 2024 Santiago Peñate Vera
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
import os
from GridCalEngine.api import *


def test_opf_ts():
    fname = os.path.join('data', 'grids', 'IEEE39_hvdc.gridcal')

    main_circuit = FileOpen(fname).open()

    power_flow_options = PowerFlowOptions(SolverType.NR,
                                          verbose=False,
                                          initialize_with_existing_solution=False,
                                          multi_core=False,
                                          dispatch_storage=True,
                                          control_q=ReactivePowerControlMode.NoControl,
                                          control_p=True,
                                          retry_with_other_methods=False)

    opf_options = OptimalPowerFlowOptions(verbose=False,
                                          solver=SolverType.LINEAR_OPF,
                                          power_flow_options=power_flow_options,
                                          mip_solver=MIPSolvers.CBC,
                                          generate_report=True)

    # HVDC dispatch on
    main_circuit.hvdc_lines[0].dispatchable = True

    opf = OptimalPowerFlowDriver(grid=main_circuit,
                                 options=opf_options)
    opf.run()

    pf_on = opf.results.hvdc_Pf[0]

    # HVDC dispatch off
    main_circuit.hvdc_lines[0].dispatchable = False

    opf = OptimalPowerFlowDriver(grid=main_circuit,
                                 options=opf_options)
    opf.run()

    pf_off = opf.results.hvdc_Pf[0]

    # check that no error or warning is generated
    assert opf.logger.error_count() == 0
    assert pf_on != pf_off
    assert np.isclose(pf_off, 0.0, atol=1e-5)