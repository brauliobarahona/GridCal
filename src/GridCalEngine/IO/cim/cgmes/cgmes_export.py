from rdflib import OWL, plugin
import rdflib

from typing import IO, Dict, Optional, Set, List
from rdflib.graph import Graph
from rdflib.namespace import RDF, RDFS, Namespace
from rdflib.plugins.parsers.RDFVOC import RDFVOC
from rdflib.plugins.serializers.xmlwriter import XMLWriter
from rdflib.serializer import Serializer
from rdflib.term import IdentifiedNode, Identifier, Literal, Node
from rdflib.util import first

import os
from GridCalEngine.IO.cim.cgmes.cgmes_circuit import CgmesCircuit
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom

plugin.register("cim_xml", Serializer, "GridCalEngine.IO.cim.cgmes.cgmes_export", "CimSerializer")

about_dict = dict()


class CimSerializer(Serializer):
    def __init__(self, store: Graph):
        super(CimSerializer, self).__init__(store)
        self.about_list = self.get_about_list()

    def serialize(
            self,
            stream: IO[bytes],
            base: Optional[str] = None,
            encoding: Optional[str] = None,
            **args,
    ):
        self.__serialized: Dict[Identifier, int] = {}
        store = self.store
        # if base is given here, use that, if not and a base is set for the graph use that
        if base is not None:
            self.base = base
        elif store.base is not None:
            self.base = store.base
        self.max_depth = args.get("max_depth", 3)
        assert self.max_depth > 0, "max_depth must be greater than 0"

        self.nm = nm = store.namespace_manager
        self.writer = writer = XMLWriter(stream, nm, encoding)
        namespaces = {}

        possible: Set[Node] = set(store.predicates()).union(
            store.objects(None, RDF.type)
        )

        for predicate in possible:
            # type error: Argument 1 to "compute_qname_strict" of "NamespaceManager" has incompatible type "Node";
            # expected "str"
            prefix, namespace, local = nm.compute_qname_strict(predicate)  # type: ignore[arg-type]
            namespaces[prefix] = namespace

        namespaces["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

        writer.push(RDFVOC.RDF)

        writer.namespaces(namespaces.items())

        subject: IdentifiedNode

        # Writing the FullModels first than delete them from the graph
        for subject in store.subjects(predicate=RDF.type,
                                      object=rdflib.URIRef(
                                          "http://iec.ch/TC57/61970-552/ModelDescription/1#FullModel")):
            self.subject(subject, 1)
            store.remove((subject, None, None))

        # Write out subjects that can not be inline
        # type error: Incompatible types in assignment (expression has type "Node", variable has type "IdentifiedNode")
        for subject in store.subjects():  # type: ignore[assignment]
            if (None, None, subject) in store:
                if (subject, None, subject) in store:
                    self.subject(subject, 1)
            else:
                self.subject(subject, 1)

        writer.pop(RDFVOC.RDF)
        stream.write("\n".encode("latin-1"))

        # Set to None so that the memory can get garbage collected.
        self.__serialized = None  # type: ignore[assignment]

    def subject(self, subject: IdentifiedNode, depth: int = 1):
        store = self.store
        writer = self.writer

        if subject not in self.__serialized:
            self.__serialized[subject] = 1
            tpe = first(store.objects(subject, RDF.type))

            try:
                # type error: Argument 1 to "qname" of "NamespaceManager" has incompatible type "Optional[Node]";
                # expected "str"
                self.nm.qname(tpe)  # type: ignore[arg-type]
            except Exception:
                tpe = None

            element = tpe or RDFVOC.Description
            writer.push(element)

            if store.value(subject, RDF.type).__str__() in self.about_list:
                writer.attribute(RDFVOC.about, self.relativize(subject))
            else:
                writer.attribute(RDFVOC.ID, self.relativize(subject))

            if (subject, None, None) in store:
                for predicate, obj in store.predicate_objects(subject):
                    if not (predicate == RDF.type and obj == tpe):
                        self.predicate(predicate, obj, depth + 1)

            writer.pop(element)

    def predicate(self, predicate, object, depth=1):
        writer = self.writer
        store = self.store
        writer.push(predicate)

        if isinstance(object, Literal):
            writer.text(object)
        elif object in self.__serialized or not (object, None, None) in store:
            writer.attribute(RDFVOC.resource, self.relativize(object))

        writer.pop(predicate)

    def get_about_list(self):
        about_list = list()
        profile = self.store.objects(None,
                                     rdflib.URIRef("http://iec.ch/TC57/61970-552/ModelDescription/1#profile"))
        for pro in profile:
            try:
                pro = pro.__str__()
                if pro == "http://entsoe.eu/CIM/EquipmentCore/3/1":
                    about_list = about_dict["eq"]
                    break
                elif pro == "http://entsoe.eu/CIM/StateVariables/4/1":
                    about_list = about_dict["sv"]
                    break
                elif pro == "http://entsoe.eu/CIM/SteadyStateHypothesis/1/1":
                    about_list = about_dict["ssh"]
                    break
                elif pro == "http://entsoe.eu/CIM/Topology/4/1":
                    about_list = about_dict["tp"]
                    break
            except:
                about_list = []

        return about_list


class CgmesExporter:
    def __init__(self, cgmes_circuit: CgmesCircuit = None):
        self.cgmes_circuit = cgmes_circuit

    def create_graph(self, profile: List[str]):
        graph = Graph()
        graph.bind("cim", Namespace("http://iec.ch/TC57/2013/CIM-schema-cim16#"))
        graph.bind("entsoe", Namespace("http://entsoe.eu/CIM/SchemaExtension/3/1#"))
        graph.bind("md", Namespace("http://iec.ch/TC57/61970-552/ModelDescription/1#"))

        full_model_list = self.cgmes_circuit.FullModel_list

        filter_props = ["scenarioTime",
                        "created",
                        "version",
                        "profile",
                        "modelingAuthoritySet",
                        "DependentOn",
                        "longDependentOnPF",
                        "Supersedes",
                        "description"]
        # populate graph with header
        for model in full_model_list:
            obj_dict = model.__dict__
            obj_id = rdflib.URIRef("urn:uuid:" + model.rdfid)
            if obj_dict.get("profile") in profile:
                for attr_name, attr_value in obj_dict.items():
                    if attr_name not in filter_props:
                        continue
                    if attr_value is None:
                        continue
                    if hasattr(attr_value, "rdfid"):
                        graph.add((rdflib.URIRef(obj_id),
                                   rdflib.URIRef(RDF.type),
                                   rdflib.URIRef("http://iec.ch/TC57/61970-552/ModelDescription/1#FullModel")))
                        graph.add((rdflib.URIRef(obj_id),
                                   rdflib.URIRef("http://iec.ch/TC57/61970-552/ModelDescription/1#Model." + attr_name),
                                   rdflib.URIRef("urn:uuid:" + attr_value.rdfid)))
                    else:
                        graph.add((rdflib.URIRef(obj_id),
                                   rdflib.URIRef(RDF.type),
                                   rdflib.URIRef("http://iec.ch/TC57/61970-552/ModelDescription/1#FullModel")))
                        graph.add((rdflib.URIRef(obj_id),
                                   rdflib.URIRef("http://iec.ch/TC57/61970-552/ModelDescription/1#Model." + attr_name),
                                   rdflib.Literal(str(attr_value))))

        return graph

    def export_to_xml(self):
        current_directory = os.path.dirname(__file__)
        relative_path_to_excel = "export_docs/CGMES_2_4_EQ_SSH_TP_SV_ConcreteClassesAllProperties.xlsx"
        absolute_path_to_excel = os.path.join(current_directory, relative_path_to_excel)

        rdf_serialization = Graph()
        rdf_serialization.parse(source=os.path.join(current_directory, "export_docs\RDFSSerialisation.ttl"),
                                format="ttl")
        enum_dict = dict()

        for s_i, p_i, o_i in rdf_serialization.triples((None, RDF.type, RDFS.Class)):
            if str(s_i).split("#")[1] == "RdfEnum":
                enum_list_dict = dict()
                for s, p, o in rdf_serialization.triples((s_i, OWL.members, None)):
                    enum_list_dict[str(o).split("#")[1]] = str(o)
                if str(s_i).split("#")[0] == "http://entsoe.eu/CIM/EquipmentCore/3/1":
                    enum_dict["eq"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/StateVariables/4/1":
                    enum_dict["sv"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/SteadyStateHypothesis/1/1":
                    enum_dict["ssh"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/Topology/4/1":
                    enum_dict["tp"] = enum_list_dict

            if str(s_i).split("#")[1] == "RdfAbout":
                about_list = list()
                for s, p, o in rdf_serialization.triples((s_i, OWL.members, None)):
                    about_list.append(str(o))
                if str(s_i).split("#")[0] == "http://entsoe.eu/CIM/EquipmentCore/3/1":
                    about_dict["eq"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/StateVariables/4/1":
                    about_dict["sv"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/SteadyStateHypothesis/1/1":
                    about_dict["ssh"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/Topology/4/1":
                    about_dict["tp"] = about_list

        profiles_info = pd.read_excel(absolute_path_to_excel, sheet_name="Profiles")

        eq_graph = self.create_graph(["http://entsoe.eu/CIM/EquipmentCore/3/1",
                                      "http://entsoe.eu/CIM/EquipmentShortCircuit/3/1",
                                      "http://entsoe.eu/CIM/EquipmentOperation/3/1"])
        ssh_graph = self.create_graph(["http://entsoe.eu/CIM/SteadyStateHypothesis/1/1"])
        tp_graph = self.create_graph(["http://entsoe.eu/CIM/Topology/4/1"])
        sv_graph = self.create_graph(["http://entsoe.eu/CIM/StateVariables/4/1"])

        graphs_dict = {
            "EQ": eq_graph,
            "SSH": ssh_graph,
            "TP": tp_graph,
            "SV": sv_graph
        }

        class_filters = {}
        for class_name in self.cgmes_circuit.classes:
            filt_class = profiles_info[profiles_info["ClassSimpleName"] == class_name]
            filters = {}

            for _, row in filt_class.iterrows():
                prop = row["Property-AttributeAssociationSimple"]
                if prop not in filters:
                    filters[prop] = {
                        "Profile": [],
                        "ClassFullName": row["ClassFullName"],
                        "Property-AttributeAssociationFull": row["Property-AttributeAssociationFull"],
                        "Type": row["Type"]
                    }
                filters[prop]["Profile"].append(row["Profile"])

            class_filters[class_name] = filters

        for class_name, filters in class_filters.items():
            objects = self.cgmes_circuit.get_objects_list(elm_type=class_name)

            for obj in objects:
                obj_dict = obj.__dict__
                obj_id = rdflib.URIRef("_" + obj.rdfid)

                for attr_name, attr_value in obj_dict.items():
                    if attr_value is None:
                        continue

                    if attr_name not in filters:
                        continue

                    attr_filters = filters[attr_name]
                    for profile in attr_filters["Profile"]:
                        graph = graphs_dict.get(profile)
                        if graph is None:
                            continue

                        attr_type = attr_filters["Type"]
                        if attr_type == "Association":
                            graph.add(
                                (obj_id, RDF.type, rdflib.URIRef(attr_filters["ClassFullName"])))
                            graph.add((rdflib.URIRef(obj_id),
                                       rdflib.URIRef(attr_filters["Property-AttributeAssociationFull"]),
                                       rdflib.URIRef("#_" + attr_value.rdfid)))
                        elif attr_type == "Enumeration":
                            enum_dict_key = profile.lower()
                            enum_dict_value = enum_dict.get(enum_dict_key)
                            enum_value = enum_dict_value.get(str(attr_value))
                            graph.add(
                                (obj_id, RDF.type, rdflib.URIRef(attr_filters["ClassFullName"])))
                            graph.add((obj_id, rdflib.URIRef(attr_filters["Property-AttributeAssociationFull"]),
                                       rdflib.URIRef(enum_value)))
                        elif attr_type == "Attribute":
                            if isinstance(attr_value, bool):
                                attr_value = str(attr_value).lower()
                            graph.add(
                                (obj_id, RDF.type, rdflib.URIRef(attr_filters["ClassFullName"])))
                            graph.add((obj_id, rdflib.URIRef(attr_filters["Property-AttributeAssociationFull"]),
                                       rdflib.Literal(str(attr_value))))

        relative_path_to_files = "export_docs/"
        absolute_path_to_files = os.path.join(current_directory, relative_path_to_files)

        eq_graph.serialize(destination=absolute_path_to_files + "eq_1.xml", format="cim_xml",
                           base="http://iec.ch/TC57/2013/CIM-schema-cim16#")
        ssh_graph.serialize(destination=absolute_path_to_files + "ssh_1.xml", format="cim_xml",
                            base="http://iec.ch/TC57/2013/CIM-schema-cim16#")
        tp_graph.serialize(destination=absolute_path_to_files + "tp_1.xml", format="cim_xml",
                           base="http://iec.ch/TC57/2013/CIM-schema-cim16#")
        sv_graph.serialize(destination=absolute_path_to_files + "sv_1.xml", format="cim_xml",
                           base="http://iec.ch/TC57/2013/CIM-schema-cim16#")


class CimExporter:
    def __init__(self, cgmes_circuit: CgmesCircuit):
        self.cgmes_circuit = cgmes_circuit
        self.namespaces = {
            "xmlns:cim": "http://iec.ch/TC57/2013/CIM-schema-cim16#",
            "xmlns:md": "http://iec.ch/TC57/61970-552/ModelDescription/1#",
            "xmlns:entsoe": "http://entsoe.eu/CIM/SchemaExtension/3/1#",
            "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        }
        self.profile_uris = {
            "EQ": ["http://entsoe.eu/CIM/EquipmentCore/3/1",
                   "http://entsoe.eu/CIM/EquipmentShortCircuit/3/1",
                   "http://entsoe.eu/CIM/EquipmentOperation/3/1"],
            "SSH": ["http://entsoe.eu/CIM/SteadyStateHypothesis/1/1"],
            "TP": ["http://entsoe.eu/CIM/Topology/4/1"],
            "SV": ["http://entsoe.eu/CIM/StateVariables/4/1"]
        }

        current_directory = os.path.dirname(__file__)
        relative_path_to_excel = "export_docs/CGMES_2_4_EQ_SSH_TP_SV_ConcreteClassesAllProperties.xlsx"
        absolute_path_to_excel = os.path.join(current_directory, relative_path_to_excel)

        rdf_serialization = Graph()
        rdf_serialization.parse(source=os.path.join(current_directory, "export_docs\RDFSSerialisation.ttl"),
                                format="ttl")

        self.enum_dict = dict()
        self.about_dict = dict()
        for s_i, p_i, o_i in rdf_serialization.triples((None, RDF.type, RDFS.Class)):
            if str(s_i).split("#")[1] == "RdfEnum":
                enum_list_dict = dict()
                for s, p, o in rdf_serialization.triples((s_i, OWL.members, None)):
                    enum_list_dict[str(o).split("#")[1]] = str(o)
                if str(s_i).split("#")[0] == "http://entsoe.eu/CIM/EquipmentCore/3/1":
                    self.enum_dict["EQ"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/StateVariables/4/1":
                    self.enum_dict["SV"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/SteadyStateHypothesis/1/1":
                    self.enum_dict["SSH"] = enum_list_dict
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/Topology/4/1":
                    self.enum_dict["TP"] = enum_list_dict
            if str(s_i).split("#")[1] == "RdfAbout":
                about_list = list()
                for s, p, o in rdf_serialization.triples((s_i, OWL.members, None)):
                    about_list.append(str(o))
                if str(s_i).split("#")[0] == "http://entsoe.eu/CIM/EquipmentCore/3/1":
                    self.about_dict["EQ"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/StateVariables/4/1":
                    self.about_dict["SV"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/SteadyStateHypothesis/1/1":
                    self.about_dict["SSH"] = about_list
                elif str(s_i).split("#")[0] == "http://entsoe.eu/CIM/Topology/4/1":
                    self.about_dict["TP"] = about_list

        profiles_info = pd.read_excel(absolute_path_to_excel, sheet_name="Profiles")

        self.class_filters = {}
        for class_name in self.cgmes_circuit.classes:
            filt_class = profiles_info[profiles_info["ClassSimpleName"] == class_name]
            filters = {}
            for _, row in filt_class.iterrows():
                prop = row["Property-AttributeAssociationSimple"]
                if prop not in filters:
                    filters[prop] = {
                        "Profile": [],
                        "ClassFullName": row["ClassFullName"],
                        "Property-AttributeAssociationFull": row["Property-AttributeAssociationFull"],
                        "Type": row["Type"]
                    }
                filters[prop]["Profile"].append(row["Profile"])
            self.class_filters[class_name] = filters

    def export(self):
        current_directory = os.path.dirname(__file__)
        with open(os.path.join(current_directory, "export_docs/eq.xml"), 'wb') as f:
            self.serialize(f, "EQ")
        with open(os.path.join(current_directory, "export_docs/ssh.xml"), 'wb') as f:
            self.serialize(f, "SSH")
        with open(os.path.join(current_directory, "export_docs/sv.xml"), 'wb') as f:
            self.serialize(f, "SV")
        with open(os.path.join(current_directory, "export_docs/tp.xml"), 'wb') as f:
            self.serialize(f, "TP")

    def serialize(self, stream, profile):
        root = ET.Element("rdf:RDF", self.namespaces)
        full_model_elements = self.generate_full_model_elements(profile)
        root.extend(full_model_elements)
        other_elements = self.generate_other_elements(profile)
        root.extend(other_elements)

        xmlstr = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        stream.write(xmlstr.encode('utf-8'))

    def generate_full_model_elements(self, profile):
        full_model_elements = []
        filter_props = {"scenarioTime": "str",
                        "created": "str",
                        "version": "str",
                        "profile": "str",
                        "modelingAuthoritySet": "str",
                        "DependentOn": "Association",
                        "longDependentOnPF": "str",
                        "Supersedes": "str",
                        "description": "str"}

        for instance in self.cgmes_circuit.FullModel_list:
            instance_dict = instance.__dict__
            if instance_dict.get("profile") in self.profile_uris[profile]:
                element = ET.Element("md:FullModel", {"rdf:about": "urn:uuid:" + instance.rdfid})
                for attr_name, attr_value in instance_dict.items():
                    if attr_name not in filter_props or attr_value is None:
                        continue
                    child = ET.Element(f"md:Model.{attr_name}")
                    if filter_props.get(attr_name) == "Association":
                        child.attrib = {"rdf:resource": "urn:uuid:" + attr_value}
                    else:
                        child.text = str(attr_value)
                    element.append(child)
                full_model_elements.append(element)
        return full_model_elements

    def in_profile(self, filters, profile):
        for k, v in filters.items():
            if profile in v["Profile"]:
                return True
        return False

    def generate_other_elements(self, profile):
        other_elements = []
        for class_name, filters in self.class_filters.items():
            objects = self.cgmes_circuit.get_objects_list(elm_type=class_name)
            if not self.in_profile(filters, profile):
                continue
            for obj in objects:
                obj_dict = obj.__dict__
                try:
                    if class_name in self.about_dict.get(profile):
                        element = ET.Element("cim:" + class_name, {"rdf:about": "_" + obj.rdfid})
                    else:
                        element = ET.Element("cim:" + class_name, {"rdf:ID": "_" + obj.rdfid})
                except:
                    element = ET.Element("cim:" + class_name, {"rdf:ID": "_" + obj.rdfid})

                for attr_name, attr_value in obj_dict.items():
                    if attr_value is None:
                        continue
                    if attr_name not in filters:
                        continue
                    attr_filters = filters[attr_name]
                    if profile not in attr_filters["Profile"]:
                        continue
                    attr_type = attr_filters["Type"]
                    prop_split = str(attr_filters["Property-AttributeAssociationFull"]).split('#')
                    if prop_split[0] == "http://entsoe.eu/CIM/SchemaExtension/3/1":
                        prop_text = "entsoe:" + prop_split[-1]
                    else:
                        prop_text = "cim:" + prop_split[-1]
                    child = ET.Element(prop_text)
                    if attr_type == "Association":
                        child.attrib = {"rdf:resource": "#_" + attr_value.rdfid}
                    elif attr_type == "Enumeration":
                        enum_dict_key = profile
                        enum_dict_value = self.enum_dict.get(enum_dict_key)
                        enum_value = enum_dict_value.get(str(attr_value))
                        child.attrib = {"rdf:resource": enum_value}
                    elif attr_type == "Attribute":
                        if isinstance(attr_value, bool):
                            attr_value = str(attr_value).lower()
                        child.text = str(attr_value)
                    element.append(child)
                other_elements.append(element)
        return other_elements
