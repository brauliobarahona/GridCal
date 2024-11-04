# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
# SPDX-License-Identifier: MPL-2.0
from __future__ import annotations
from typing import TYPE_CHECKING, Union
import numpy as np
from GridCalEngine.Devices.multi_circuit import MultiCircuit
from GridCalEngine.DataStructures.numerical_circuit import compile_numerical_circuit_at
from GridCalEngine.Simulations.ContingencyAnalysis.contingency_analysis_results import ContingencyAnalysisResults
from GridCalEngine.Simulations.PowerFlow.power_flow_worker import multi_island_pf_nc
from GridCalEngine.Simulations.PowerFlow.power_flow_options import PowerFlowOptions, SolverType
from GridCalEngine.Simulations.LinearFactors.linear_analysis import LinearAnalysis, LinearMultiContingencies
from GridCalEngine.Simulations.ContingencyAnalysis.contingency_analysis_options import ContingencyAnalysisOptions
from GridCalEngine.basic_structures import Logger

if TYPE_CHECKING:
    from GridCalEngine.Simulations.ContingencyAnalysis.contingency_analysis_driver import ContingencyAnalysisDriver


def nonlinear_contingency_analysis(grid: MultiCircuit,
                                   options: ContingencyAnalysisOptions,
                                   linear_multiple_contingencies: LinearMultiContingencies,
                                   calling_class: ContingencyAnalysisDriver,
                                   t: Union[None, int] = None,
                                   t_prob: float = 1.0,
                                   logger: Logger | None = None,) -> ContingencyAnalysisResults:
    """
    Run a contingency analysis using the power flow options
    :param grid: MultiCircuit
    :param options: ContingencyAnalysisOptions
    :param linear_multiple_contingencies: LinearMultiContingencies
    :param calling_class: ContingencyAnalysisDriver
    :param t: time index, if None the snapshot is used
    :param t_prob: probability of te time
    :param logger: logging object
    :return: returns the results (ContingencyAnalysisResults)
    """
    if logger is None:
        logger = Logger()

    # set the numerical circuit
    numerical_circuit = compile_numerical_circuit_at(grid, t_idx=t)

    if options.pf_options is None:
        pf_opts = PowerFlowOptions(solver_type=SolverType.DC,
                                   ignore_single_node_islands=True)

    else:
        pf_opts = options.pf_options

    area_names, bus_area_indices, F, T, hvdc_F, hvdc_T = grid.get_branch_areas_info()

    # declare the results
    results = ContingencyAnalysisResults(ncon=len(linear_multiple_contingencies.contingency_groups_used),
                                         nbr=numerical_circuit.nbr,
                                         nbus=numerical_circuit.nbus,
                                         branch_names=numerical_circuit.branch_names,
                                         bus_names=numerical_circuit.bus_names,
                                         bus_types=numerical_circuit.bus_types,
                                         con_names=linear_multiple_contingencies.get_contingency_group_names())

    # get contingency groups dictionary
    cg_dict = grid.get_contingency_group_dict()
    calc_branches = grid.get_branches_wo_hvdc()
    mon_idx = numerical_circuit.branch_data.get_monitor_enabled_indices()

    # run 0
    pf_res_0 = multi_island_pf_nc(nc=numerical_circuit,
                                  options=pf_opts)

    if options.use_srap:

        # we need the PTDF for this
        linear_analysis = LinearAnalysis(numerical_circuit=numerical_circuit,
                                         distributed_slack=options.lin_options.distribute_slack,
                                         correct_values=options.lin_options.correct_values)
        linear_analysis.run()

        linear_multiple_contingencies.compute(lodf=linear_analysis.LODF,
                                              ptdf=linear_analysis.PTDF,
                                              ptdf_threshold=options.lin_options.ptdf_threshold,
                                              lodf_threshold=options.lin_options.lodf_threshold,
                                              prepare_for_srap=options.use_srap)

        PTDF = linear_analysis.PTDF

    else:
        PTDF = None

    available_power = numerical_circuit.generator_data.get_injections_per_bus().real

    # for each contingency group
    for ic, contingency_group in enumerate(linear_multiple_contingencies.contingency_groups_used):

        # get the group's contingencies
        contingencies = cg_dict[contingency_group.idtag]

        # set the status
        numerical_circuit.set_con_or_ra_status(contingencies)

        # report progress
        if t is None and calling_class is not None:
            calling_class.report_text(f'Contingency group: {contingency_group.name}')
            calling_class.report_progress2(ic, len(linear_multiple_contingencies.contingency_groups_used) * 100)

        # run
        pf_res = multi_island_pf_nc(nc=numerical_circuit,
                                    options=pf_opts,
                                    V_guess=pf_res_0.voltage,
                                    logger=logger)

        results.Sf[ic, :] = pf_res.Sf
        results.Sbus[ic, :] = pf_res.Sbus
        results.loading[ic, :] = pf_res.loading
        results.voltage[ic, :] = pf_res.voltage
        multi_contingency = linear_multiple_contingencies.multi_contingencies[ic] if options.use_srap else None

        results.report.analyze(t=t,
                               t_prob=t_prob,
                               mon_idx=mon_idx,
                               numerical_circuit=numerical_circuit,
                               base_flow=np.abs(pf_res_0.Sf),
                               base_loading=np.abs(pf_res_0.loading),
                               contingency_flows=np.abs(pf_res.Sf),
                               contingency_loadings=np.abs(pf_res.loading),
                               contingency_idx=ic,
                               contingency_group=contingency_group,
                               using_srap=options.use_srap,
                               srap_ratings=numerical_circuit.branch_data.protection_rates,
                               srap_max_power=options.srap_max_power,
                               srap_deadband=options.srap_deadband,
                               contingency_deadband=options.contingency_deadband,
                               multi_contingency=multi_contingency,
                               PTDF=PTDF,
                               available_power=available_power,
                               srap_used_power=results.srap_used_power,
                               F=F,
                               T=T,
                               bus_area_indices=bus_area_indices,
                               area_names=area_names,
                               top_n=options.srap_top_n)

        # set the status
        numerical_circuit.set_con_or_ra_status(contingencies, revert=True)

        if calling_class is not None:
            if calling_class.is_cancel():
                return results

    return results
