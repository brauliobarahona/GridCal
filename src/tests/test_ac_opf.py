# GridCal
# Copyright (C) 2015 - 2024 Santiago Peñate Vera
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
import numpy as np
import GridCalEngine.api as gce
from GridCalEngine.Simulations.OPF.NumericalMethods.ac_opf import ac_optimal_power_flow, NonlinearOPFResults


def case9() -> NonlinearOPFResults:
    """
    Test case9 from matpower
    :return:
    """
    cwd = os.getcwd()
    print(cwd)

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..'))
    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case9.m')

    grid = gce.FileOpen(file_path).open()
    nc = gce.compile_numerical_circuit_at(grid)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, tolerance=1e-8)
    return ac_optimal_power_flow(nc=nc, pf_options=pf_options)


def case14() -> NonlinearOPFResults:
    """
    Test case14 from matpower
    :return:
    """
    cwd = os.getcwd()
    print(cwd)

    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..'))
    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case14.m')

    grid = gce.FileOpen(file_path).open()
    nc = gce.compile_numerical_circuit_at(grid)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, tolerance=1e-8)
    return ac_optimal_power_flow(nc=nc, pf_options=pf_options)


def case_pegase89() -> NonlinearOPFResults:
    """
    Pegase89
    """
    cwd = os.getcwd()
    print(cwd)
    # Go back two directories
    new_directory = os.path.abspath(os.path.join(cwd, '..', '..'))
    file_path = os.path.join(new_directory, 'Grids_and_profiles', 'grids', 'case89pegase.m')

    grid = gce.FileOpen(file_path).open()
    nc = gce.compile_numerical_circuit_at(grid)
    pf_options = gce.PowerFlowOptions(solver_type=gce.SolverType.NR, tolerance=1e-8)
    return ac_optimal_power_flow(nc=nc, pf_options=pf_options)


def test_ieee9():
    vm_test = [1.09995, 1.097362, 1.086627, 1.094186, 1.084424, 1.099999, 1.089488, 1.099999, 1.071731]
    va_test = [0.0, 0.0854008, 0.05670578, -0.0429894, -0.0695051, 0.0105133, -0.0208879, 0.0157974, -0.0805577]
    Pg_test = [0.897986, 1.343206, 0.941874]
    Qg_test = [0.129387, 0.00047729, -0.226197]
    res = case9()
    assert np.allclose(res.Vm, vm_test, atol=1e-3)
    assert np.allclose(res.Va, va_test, atol=1e-3)
    assert np.allclose(res.Pg, Pg_test, atol=1e-3)
    assert np.allclose(res.Qg, Qg_test, atol=1e-3)
    # pass


def test_ieee14():
    vm_test = [1.05999995, 1.04075308, 1.01562523, 1.01446086, 1.01636258,
               1.05999951, 1.04634682, 1.05999962, 1.043699, 1.03913656,
               1.04600928, 1.04482001, 1.0399485, 1.02388846]
    va_test = [0.0, -0.07020258, -0.17323969, -0.15123061, -0.12965054,
               -0.22146884, -0.19526525, -0.18177315, -0.22684304, -0.23095753,
               -0.22848023, -0.23619049, -0.23706053, -0.24912998]
    Pg_test = [1.943300, 0.3671917, 0.2874277, 0.00000105, 0.08495043]
    Qg_test = [0.00000288, 0.2368517, 0.2412688, 0.1154574, 0.08273013]
    res = case14()
    assert np.allclose(res.Vm, vm_test, atol=1e-3)
    assert np.allclose(res.Va, va_test, atol=1e-3)
    assert np.allclose(res.Pg, Pg_test, atol=1e-3)
    assert np.allclose(res.Qg, Qg_test, atol=1e-3)


def test_pegase89():
    vm_test = [1.0074489678886993, 1.0641454564893884, 1.048202859439909, 1.0565276710947504, 1.0581784225132953,
               1.0480692132039073, 1.0336685100981355, 1.0094232387161937, 1.0605956839842463, 1.023404846675702,
               1.0479220538735987, 1.0324801136323596, 1.048308120422882, 1.0369543843496938, 1.0187387242451165,
               1.0539294037930693, 1.0134767666853803, 1.0230875973052609, 1.0668509909156727, 1.0312337348368426,
               1.0392126618247808, 1.0347571026970217, 1.0243726413557317, 1.052168238336803, 0.9991376984264492,
               1.053438096130044, 0.9953989471580725, 1.0999999980561883, 1.008355081147682, 1.0605956967114194,
               1.0298545170418907, 1.0558034115951542, 1.0626667816728435, 1.0481389906046095, 1.0525828286129002,
               1.0096533635374116, 1.0431259406638123, 1.0592941342766384, 1.0534599436752854, 1.0468920782866817,
               1.049563504962298, 1.060784128904872, 1.0507408513430456, 1.0605930006771913, 1.0626062283572166,
               1.0399733037495327, 1.048885844505469, 1.0511189917391615, 1.0106894175854413, 1.052690647869497,
               1.0387941261570273, 1.0851522813641632, 1.0215253370717372, 1.0387459427386485, 0.9829326046583633,
               1.0567934517341517, 0.9984879300879893, 1.0792148730265942, 1.015004068979941, 1.0610455301051265,
               1.0869086053610795, 0.9741992835906887, 1.0278654567416745, 0.9768385317437996, 1.0592941342766384,
               1.0274570470674849, 1.0541045724405247, 1.0491833490916747, 1.017106388983106, 1.071693148250231,
               1.0599335799217529, 1.0181150442236566, 1.0113424971044032, 1.01108581740185, 1.0851522813641632,
               1.0524772134106943, 1.0369462165905086, 1.0542238240428443, 1.0133768128603122, 1.053481564280021,
               1.0329063530056604, 1.0259995516333784, 1.0175104538116544, 1.0242391192902984, 1.0664632128292977,
               1.0123415076851068, 1.0133449233135947, 1.0322158006198487, 1.0599851774809217]

    va_test = [-0.06465118034151815, -0.10640980510226476, -0.1399266414110869, -0.012246233082224034,
               -0.012651790978506092, -0.12331161558389342, 1.2741537381898505e-17, -0.17667496340489738,
               -0.03125007768901637, -0.05786401585447236, -0.025494195772856332, -0.03025956985900047,
               -0.10017469224696054, -0.1650571882544151, -0.06218209850645626, -0.127665150391653,
               -0.05332731438249186, -0.058282486470438, -0.10496970108354091, -0.1811317587688065,
               0.007238674497978351, 0.04220342680810039, -0.21274999895852761, 0.06759479802436287,
               -0.07066863799320257, -0.15429532226303458, -0.07160038013454476, -0.14752311330262083,
               -0.06585737430879415, -0.03125010568909018, -0.16095715532678836, -0.04201665748864401,
               -0.1260280164546343, -0.12279709711707061, -0.14196510121387454, -0.1760715331662262,
               0.01753035301499174, -0.12855970802894515, -0.153943255275001, -0.1601801375455872, -0.16379705973226913,
               -0.12228857640086133, -0.17193559316925203, -0.031249857688459774, -0.12601059755101937,
               -0.15989916940122137, -0.09380414754645358, 0.07360569177423593, -0.07712131519454316,
               -0.14133426925841636, 0.011936248115483878, -0.14954131932308126, -0.05616974434253238,
               0.011940262301677882, -0.09263296968420562, -0.011582171466560898, -0.06508613754090174,
               -0.1467844275004424, -0.05566657715049195, -0.01052822279279031, -0.1519424038284098,
               -0.10529961640415858, -0.05465173356025716, -0.10685178436723765, -0.12855970802894515,
               -0.04284941283591582, -0.17532616612170582, 0.17856371546907676, -0.041033692188213115,
               -0.10085427830726935, -0.011547697554950465, -0.07710259477734246, -0.06202528637180118,
               -0.058163145931748435, -0.14954131932308126, -0.020960528480590365, -0.1654424664485851,
               -0.12690276731341427, -0.0584125137144, 0.3691137847091673, -0.02920978205584944, -0.05894613128302571,
               -0.05201455196572229, -0.2132953077784708, -0.07994849287907628, -0.05411312240639907,
               -0.054035805426684604, -0.1769520600066093, -0.011508102305939516]

    Pg_test = [16.933573321147044, 12.102199666613217, 1.6667006341358497, 6.666704387302476, 0.509499156272972,
               0.21229782375830258, 5.320233745735995, 3.333409135834844, 0.9999985247285276, 2.2267723215553645,
               5.999997139830848, 2.2266753310838365]

    Qg_test = [5.277412923694324, 6.618986753297607, 2.2815996838399255, 3.7236056370014854, -0.29809756674253635,
               0.04179455966592346, -1.8996743248262995, 3.55863879355706, -0.06639703271324378, 2.7419484992706997,
               1.25513044433617, 2.7419485085973423]

    res = case_pegase89()
    assert np.allclose(res.Vm, vm_test, atol=1e-3)
    assert np.allclose(res.Va, va_test, atol=1e-3)
    assert np.allclose(res.Pg, Pg_test, atol=1e-3)
    assert np.allclose(res.Qg, Qg_test, atol=1e-3)
