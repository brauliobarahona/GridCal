import os
import GridCalEngine.api as gce
from GridCalEngine.DataStructures.numerical_circuit import compile_numerical_circuit_at
from GridCalEngine.Simulations.OPF.NumericalMethods.ac_opf_bound_slacks import run_nonlinear_opf, ac_optimal_power_flow
from GridCalEngine.enumerations import TransformerControlType


def example_3bus_acopf():
    """

    :return:
    """

    grid = gce.MultiCircuit()

    b1 = gce.Bus(is_slack=True)
    b2 = gce.Bus()
    b3 = gce.Bus()

    grid.add_bus(b1)
    grid.add_bus(b2)
    grid.add_bus(b3)

    grid.add_line(gce.Line(bus_from=b1, bus_to=b2, name='line 1-2', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b2, bus_to=b3, name='line 2-3', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b3, bus_to=b1, name='line 3-1_1', r=0.001, x=0.05, rate=100))
    # grid.add_line(Line(bus_from=b3, bus_to=b1, name='line 3-1_2', r=0.001, x=0.05, rate=100))

    grid.add_load(b3, gce.Load(name='L3', P=50, Q=40))
    grid.add_generator(b1, gce.Generator('G1', vset=1.00, Cost=1.0, Cost2=2.0))
    grid.add_generator(b2, gce.Generator('G2', P=10, vset=0.995, Cost=1.0, Cost2=3.0))

    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_tolerance=1e-8, ips_iterations=25)
    options = gce.PowerFlowOptions(gce.SolverType.NR, verbose=False)
    power_flow = gce.PowerFlowDriver(grid, options)
    power_flow.run()

    # print('\n\n', grid.name)
    # print('\tConv:\n', power_flow.results.get_bus_df())
    # print('\tConv:\n', power_flow.results.get_branch_df())

    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=3)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True)


def case_3bus():
    """

    :return:
    """

    grid = gce.MultiCircuit()

    b1 = gce.Bus(is_slack=True)
    b2 = gce.Bus()
    b3 = gce.Bus()

    grid.add_bus(b1)
    grid.add_bus(b2)
    grid.add_bus(b3)

    #grid.add_line(gce.Line(bus_from=b1, bus_to=b2, name='Line 1-2', r=0.001, x=0.05, rate=100))
    #grid.add_line(gce.Line(bus_from=b2, bus_to=b3, name='Line 2-3', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b3, bus_to=b1, name='Line 3-1', r=0.001, x=0.05, rate=100))

    grid.add_load(b3, gce.Load(name='L3', P=50, Q=20))
    grid.add_generator(b1, gce.Generator('G1', vset=1.00, Cost=1.0, Cost2=2.0))
    grid.add_generator(b2, gce.Generator('G2', P=10, vset=0.995, Cost=1.0, Cost2=3.0))

    tr1 = gce.Transformer2W(b1, b2, 'Trafo 1', control_mode=TransformerControlType.PtQt,
                            tap_module=1.01, tap_phase=0.02, r=0.001, x=0.05, tap_phase_max=0.5, tap_module_max=1.1,
                            tap_phase_min=-0.5, tap_module_min=0.9, rate=100)

    grid.add_transformer2w(tr1)

    tr2 = gce.Transformer2W(b2, b3, 'Trafo 2', control_mode=TransformerControlType.PtV,
                            tap_module=1.01, tap_phase=+0.02, r=0.004, x=0.08, tap_phase_max=0.03, tap_module_max=1.02,
                            tap_phase_min=-0.02, tap_module_min=0.98, rate=100)
    grid.add_transformer2w(tr2)

    options = gce.PowerFlowOptions(gce.SolverType.NR, verbose=False)
    power_flow = gce.PowerFlowDriver(grid, options)
    power_flow.run()

    # print('\n\n', grid.name)
    # print('\tConv:\n', power_flow.results.get_bus_df())
    # print('\tConv:\n', power_flow.results.get_branch_df())

    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, max_iter=50, verbose=3)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, plot_error=True)
    nc = compile_numerical_circuit_at(circuit=grid)


def linn5bus_example():
    """
    Grid from Lynn Powel's book
    """
    # declare a circuit object
    grid = gce.MultiCircuit()

    # Add the buses and the generators and loads attached
    bus1 = gce.Bus('Bus 1', vnom=20)
    # bus1.is_slack = True  # we may mark the bus a slack
    grid.add_bus(bus1)

    # add a generator to the bus 1
    gen1 = gce.Generator('Slack Generator', vset=1.0, Pmin=0, Pmax=1000,
                         Qmin=-1000, Qmax=1000, Cost=15, Cost2=0.0)

    grid.add_generator(bus1, gen1)

    # add bus 2 with a load attached
    bus2 = gce.Bus('Bus 2', vnom=20)
    grid.add_bus(bus2)
    grid.add_load(bus2, gce.Load('load 2', P=40, Q=20))

    # add bus 3 with a load attached
    bus3 = gce.Bus('Bus 3', vnom=20)
    grid.add_bus(bus3)
    grid.add_load(bus3, gce.Load('load 3', P=25, Q=15))

    # add bus 4 with a load attached
    bus4 = gce.Bus('Bus 4', vnom=20)
    grid.add_bus(bus4)
    grid.add_load(bus4, gce.Load('load 4', P=40, Q=20))

    # add bus 5 with a load attached
    bus5 = gce.Bus('Bus 5', vnom=20)
    grid.add_bus(bus5)
    grid.add_load(bus5, gce.Load('load 5', P=50, Q=20))

    # add Lines connecting the buses
    #grid.add_line(gce.Line(bus1, bus2, name='line 1-2', r=0.05, x=0.11, b=0.02, rate=1000))
    grid.add_line(gce.Line(bus1, bus3, name='line 1-3', r=0.05, x=0.11, b=0.02, rate=1000))
    grid.add_line(gce.Line(bus1, bus5, name='line 1-5', r=0.03, x=0.08, b=0.02, rate=1000))
    grid.add_line(gce.Line(bus2, bus3, name='line 2-3', r=0.04, x=0.09, b=0.02, rate=1000))
    grid.add_line(gce.Line(bus2, bus5, name='line 2-5', r=0.04, x=0.09, b=0.02, rate=1000))
    grid.add_line(gce.Line(bus3, bus4, name='line 3-4', r=0.06, x=0.13, b=0.03, rate=1000))
    grid.add_line(gce.Line(bus4, bus5, name='line 4-5', r=0.04, x=0.09, b=0.02, rate=1000))

    tr1 = gce.Transformer2W(bus1, bus2, 'Trafo 1', control_mode=TransformerControlType.PtQt,
                            tap_module=0.95, tap_phase=-0.02, r=0.05, x=0.11, tap_phase_max=0.5, tap_module_max=1.1,
                            tap_phase_min=-0.5, tap_module_min=0.9, rate=1000)

    grid.add_transformer2w(tr1)

    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=1)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, plot_error=True)


def two_grids_of_3bus():
    """
    3 bus grid two times
    for solving islands at the same time
    """
    grid = gce.MultiCircuit()

    # 3 bus grid
    b1 = gce.Bus(is_slack=True)
    b2 = gce.Bus()
    b3 = gce.Bus()

    grid.add_bus(b1)
    grid.add_bus(b2)
    grid.add_bus(b3)

    grid.add_line(gce.Line(bus_from=b1, bus_to=b2, name='line 1-2', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b2, bus_to=b3, name='line 2-3', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b3, bus_to=b1, name='line 3-1_1', r=0.001, x=0.05, rate=100))
    # grid.add_line(Line(bus_from=b3, bus_to=b1, name='line 3-1_2', r=0.001, x=0.05, rate=100))

    grid.add_load(b3, gce.Load(name='L3', P=50, Q=20))
    grid.add_generator(b1, gce.Generator('G1', vset=1.00, Cost=1.0, Cost2=2.0))
    grid.add_generator(b2, gce.Generator('G2', P=10, vset=0.995, Cost=1.0, Cost2=3.0))

    # 3 bus grid
    b11 = gce.Bus(is_slack=True)
    b21 = gce.Bus()
    b31 = gce.Bus()

    grid.add_bus(b11)
    grid.add_bus(b21)
    grid.add_bus(b31)

    grid.add_line(gce.Line(bus_from=b11, bus_to=b21, name='line 1-2 (2)', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b21, bus_to=b31, name='line 2-3 (2)', r=0.001, x=0.05, rate=100))
    grid.add_line(gce.Line(bus_from=b31, bus_to=b11, name='line 3-1 (2)', r=0.001, x=0.05, rate=100))

    grid.add_load(b31, gce.Load(name='L3 (2)', P=50, Q=20))
    grid.add_generator(b11, gce.Generator('G1 (2)', vset=1.00, Cost=1.0, Cost2=2.0))
    grid.add_generator(b21, gce.Generator('G2 (2)', P=10, vset=0.995, Cost=1.0, Cost2=1.0))

    hvdc = gce.HvdcLine(b11, b1, r=0.001, rate=0.4)
    grid.add_hvdc(hvdc)
    hvdc2 = gce.HvdcLine(b11, b1, r=0.001, rate=0.4)
    grid.add_hvdc(hvdc2)

    options = gce.PowerFlowOptions(gce.SolverType.NR, verbose=False)
    power_flow = gce.PowerFlowDriver(grid, options)
    power_flow.run()

    # print('\n\n', grid.name)
    # print('\tConv:\n', power_flow.results.get_bus_df())
    # print('\tConv:\n', power_flow.results.get_branch_df())

    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_tolerance=1e-5, ips_iterations=25)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=3, max_iter=25)
    # run_nonlinear_opf(grid=grid, pf_options=pf_options, plot_error=True)
    island = compile_numerical_circuit_at(circuit=grid, t_idx=None)

    island_res = ac_optimal_power_flow(nc=island,
                                       pf_options=pf_options,
                                       opf_options=opf_options,
                                       debug=False,
                                       use_autodiff=False,
                                       plot_error=True)


def case9():
    """
    IEEE9
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))
    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case9.m')

    grid = gce.FileOpen(file_path).open()
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=1, tolerance=1e-10)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, plot_error=True)


def case14():
    """
    IEEE14
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case14.m')

    grid = gce.FileOpen(file_path).open()

    grid.transformers2w[0].control_mode = TransformerControlType.PtQt
    grid.transformers2w[1].control_mode = TransformerControlType.Pf
    grid.transformers2w[2].control_mode = TransformerControlType.V

    #grid.delete_line(grid.lines[0])
    #grid.delete_line(grid.lines[1])
    for ll in range(len(grid.lines)):
        grid.lines[ll].monitor_loading = True

    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR)
    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, ips_tolerance=1e-7,
                                              ips_iterations=50, verbose=1)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=True)


def case_gb():
    """
    GB
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'GB Network.gridcal')

    grid = gce.FileOpen(file_path).open()
    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_iterations=80, ips_tolerance=1e-6)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=1)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=True)


def case_pegase89():
    """
    Pegase89
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case89pegase.m')

    grid = gce.FileOpen(file_path).open()

    #nc = compile_numerical_circuit_at(grid)
    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_iterations=100, ips_tolerance=1e-7)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=1)
    #ac_optimal_power_flow(nc=nc, pf_options=pf_options, plot_error=True)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=True)
    grid.get_bus_branch_connectivity_matrix()
    nc = compile_numerical_circuit_at(grid)
    print('')


def case300():
    """
    case300.m
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case300.m')

    grid = gce.FileOpen(file_path).open()
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=1, max_iter=50)
    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_iterations=100)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=False)


def casepegase13k():
    """
    Solves for pf_init=False in about a minute and 130 iterations.
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case13659pegase.m')

    grid = gce.FileOpen(file_path).open()

    options = gce.PowerFlowOptions(gce.SolverType.NR, verbose=False)
    power_flow = gce.PowerFlowDriver(grid, options)
    power_flow.run()

    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_tolerance=1e-6, ips_iterations=70)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=3)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=True)


def casehvdc():
    """
    IEEE14
    """
    cwd = os.getcwd()

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..', '..'))

    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'ESPGRID.gridcal')

    grid = gce.FileOpen(file_path).open()

    options = gce.PowerFlowOptions(gce.SolverType.NR, verbose=False)
    power_flow = gce.PowerFlowDriver(grid, options)
    power_flow.run()

    opf_options = gce.OptimalPowerFlowOptions(solver=gce.SolverType.NONLINEAR_OPF, verbose=1, ips_iterations=100, ips_tolerance=1e-6)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, verbose=3)
    run_nonlinear_opf(grid=grid, pf_options=pf_options, opf_options=opf_options, plot_error=True, pf_init=True)

if __name__ == '__main__':
    # example_3bus_acopf()
    # case_3bus()
    # linn5bus_example()
    # two_grids_of_3bus()
    # case9()
    # case14()
    # case_gb()
    # case6ww()
    # case_pegase89()
    # case300()
    casepegase13k()
    #casehvdc()