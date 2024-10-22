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

from typing import Union
from GridCalEngine.Devices.Parents.editable_device import EditableDevice, DeviceType
from GridCalEngine.Devices.Aggregation.remedial_action_group import RemedialActionGroup


class RemedialAction(EditableDevice):
    """
    The RemedialAction object
    """

    def __init__(self,
                 idtag: Union[str, None] = None,
                 device_idtag='',
                 name="Remedial action",
                 code='',
                 prop='active',
                 value=0.0,
                 group: Union[None, RemedialActionGroup] = None):
        """
        RemedialAction
        :param idtag: String. Element unique identifier
        :param name: String. Contingency name
        :param code: String. Contingency code name
        :param prop: String. Property to modify when contingency is triggered out
        :param value: Float. Property value to apply when contingency happens
        :param group: RemedialActionGroup. RemedialAction group
        """

        EditableDevice.__init__(self,
                                idtag=idtag,
                                code=code,
                                name=name,
                                device_type=DeviceType.RemedialActionDevice)

        # Contingency type
        self.device_idtag = device_idtag
        self._prop = prop
        self._value = value
        self._group: RemedialActionGroup = group
        self._allowed_properties = ['active', '%']

        self.register(key='device_idtag', units='', tpe=str, definition='Unique ID', editable=False)
        self.register(key='prop', units='', tpe=str,
                      definition=f'Name of the object property to change  {", ".join(self._allowed_properties)}')
        self.register(key='value', units='', tpe=float, definition='Property value')
        self.register(key='group', units='', tpe=DeviceType.RemedialActionGroupDevice,
                      definition='Remedial action group')

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = val

    @property
    def prop(self) -> str:
        """
        Property to modify when contingency is triggered out
        :return:
        """
        return self._prop

    @prop.setter
    def prop(self, val: str):
        if val in self._allowed_properties:
            self._prop = val
        else:
            print(f"Not allowed property {val}, allowed: " + "".join(self._allowed_properties))

    @property
    def value(self) -> float:
        """
        Property value to apply when contingency happens
        :return:
        """
        return self._value

    @value.setter
    def value(self, val: float):
        self._value = val

    @property
    def group(self) -> RemedialActionGroup:
        """
        Contingency group
        :return:
        """
        return self._group

    @group.setter
    def group(self, val: RemedialActionGroup):
        self._group = val

    @property
    def category(self):
        """

        :return:
        """
        return self.group.category

    @category.setter
    def category(self, val):
        # self.group.category = val
        pass
