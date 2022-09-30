import codecs
import py2neo
import csv
import neotime
import time
import json
import jsonlines
import configparser
import pathlib
import os

from utils import LexicalNormaliser

from dateutil.parser import parse as parse_date
from py2neo import Graph
from py2neo.data import Node, Relationship
from environs import Env


CURRENT_PATH = current_path = pathlib.Path(__file__).parent.resolve()


env = Env()
env.read_env(os.path.join(CURRENT_PATH.parent.parent, ".env"))

# A document that stores index, tokens and mentions.
# Initially has no mentions.
class Document:

    """
    A document that represents a single document in the dataset.

    Attributes:
        index (Integer): The document index.
        mentions (List): A list of Mention objects appearing in this document.
        structured_fields (Dict): A dictionary of the structured fields appearing in this document.
        tokens (List): A list of the tokens in this document.
        triples (List): A list of Triple objects appearing in this document.
    """

    def __init__(self, index, tokens, structured_fields):
        self.index = index
        self.tokens = tokens
        self.mentions = []
        self.triples = []
        self.structured_fields = structured_fields

    def add_mention(self, mention):
        """
        Add a mention to this document.

        Args:
            mention (Mention): The mention to add.
        """
        assert mention.end <= len(
            self.tokens
        ), "Mention end exceeds document length"
        self.mentions.append(mention)

    def add_triple(self, triple):
        """Add a triple to this document."""
        self.triples.append(triple)

    def __str__(self):
        s = ""
        s += "Index: %d\n" % (self.index)
        s += "Tokens: %s \n" % (self.tokens)
        s += "Structured fields:\n"
        for field, value in self.structured_fields.items():
            s += "%s: %s\n" % (field.ljust(20), value)
        s += "Mentions:\n"
        for m in self.mentions:
            s += str(m)
            s += "\n"
        s += "Triples:\n"
        for t in self.triples:
            s += str(t)
            s += "\n"
        return s


class Mention:

    """
    A Mention, which takes the form {start: <start index>, end: <end index>, labels: [label1, label2, label3]}

    Attributes:
            start (Integer): The word index of the start of this phrase with reference to the sentence in which it appeared.
        end (Integer): Same as above, but for the end.
        labels (List): A list of EntityClasses of this mention.
        phrase_type (String): The type of phrase, i.e. "Mention".
        text (String): The mention text, e.g. "broken".
    """

    def __init__(self, start, end, labels, text=""):
        self.start = start
        self.end = end
        self.labels = labels
        self.text = text
        self.phrase_type = "Mention"

    def short_print(self):
        return "[M] %s" % (", ".join([l.name for l in self.labels]))

    def __str__(self):
        return '[Mention] Text: "%s", Start: %s, End: %s, Labels: %s' % (
            self.text,
            str(self.start).ljust(3),
            str(self.end).ljust(3),
            ", ".join([l.name for l in self.labels]),
        )

    __repr__ = __str__


class Triple:

    """

    # A triple, which connects a subject with an object via a relation.

    Attributes:
        obj (Mention): The object Mention.
        subj (Mention): The subject Mention.
        verb (Phrase): The verb phrase.
    """

    def __init__(self, subj, verb, obj):
        self.subj = subj
        self.verb = verb
        self.obj = obj

    def __str__(self):
        return "(%s)-[%s]->(%s)" % (
            self.subj.short_print(),
            self.verb.short_print(),
            self.obj.short_print(),
        )


class EntityCategory:

    """An Entity, which stores the entity name as a string, and a reference to its parent.

    Attributes:
        base_class (EntityCategory): The EnityCategory corresponding to the base class of this entity, e.g. "Item".
        name (String): The name of this category.
        parent (EntityCategory): The EntityCategory corresponding to the parent of this EntityCategory.
    """

    def __init__(self, name, parent_ref, base_class):
        self.name = name
        self.parent = parent_ref
        self.base_class = base_class

    def __str__(self):
        return "( %s ) -> ( %s )" % (
            self.name,
            self.parent if self.parent is not None else "(None)",
        )

    __repr__ = __str__


class Hierarchy:

    """

    A Hierarchy, which stores the concept hierarchy in a list of entities. Each entity has a reference to its parent entity.

    Attributes:
        entity_classes (List): A list of enity classes in this hierarchy.
    """

    def __init__(self, f):
        self.entity_classes = self.read_hierarchy(f)

    def read_hierarchy(self, hierarchy_file):
        """

        Reads the hierarchy file and generates the hierarchy.

        Args:
            hierarchy_file (String): The filename containing the hierarchy. Should be indented
            when going down a level in the hierarchy.

        Returns:
            hierarchy: The generated hierarchy.
        """

        def leading_spaces(line):
            # Retrieve the number of leading spaces in order to determine hierarchy level.
            return len(line) - len(line.strip(" "))

        current_parents = []
        current_indent = 0

        entities = {}

        hierarchy = []
        with open(hierarchy_file, "r") as f:
            for line in f:
                line = line.rstrip()
                indent = leading_spaces(line)
                category = line.strip()

                if indent == 0:
                    current_parents = [category]
                else:
                    if indent < current_indent:
                        for x in range(0, current_indent - indent + 1):
                            current_parents.pop()
                        current_parents.append(category)
                    if indent == current_indent:
                        current_parents.pop()
                    if indent >= current_indent:
                        current_parents.append(category)

                base_class = current_parents[0].capitalize()

                parent_entity = (
                    current_parents[-2] if len(current_parents) > 1 else None
                )
                if parent_entity is None:
                    parent_entity_ref = None
                else:
                    parent_entity_ref = entities[parent_entity]

                this_entity = current_parents[-1]
                if this_entity in entities:
                    entity_ref = entities[this_entity]
                else:
                    entity_ref = EntityCategory(
                        this_entity, parent_entity_ref, base_class
                    )
                    entities[this_entity] = entity_ref

                hierarchy.append(entity_ref)
                current_indent = indent

        return hierarchy


class Delay AccountingDataset:

    """An Delay Accounting Dataset, which stores the data from the Delay Accounting csv.

    Attributes:
        delay_accounting_events (List): A list of rows from the Delay Accounting csv.
        floc_to_delay_accounting_events (Dict): A mapping of FLOC -> [ delay_accounting events for that FLOC ]
    """

    def __init__(self, delay_accounting_data_file):
        self.delay_accounting_events = self.read_dataset(delay_accounting_data_file)
        # print(self.delay_accounting_events)
        self.floc_to_delay_accounting_events = self.build_floc_mapping()
        # print(self.floc_to_delay_accounting_events)

    def read_dataset(self, delay_accounting_data_file):
        delay_accounting_events = []
        with open(delay_accounting_data_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                delay_accounting_events.append({k: row[k] for k in row})
        return delay_accounting_events

    def build_floc_mapping(self):
        """Builds a mapping of FLOC -> [ delay_accounting events for that FLOC].

        Returns:
            Dict: A mapping as above.
        """
        floc_to_delay_accounting_events = {}
        for delay_accounting_event in self.delay_accounting_events:
            floc = delay_accounting_event["EQUIPMENT_ID_CAUSE_LOCATION"]
            if floc not in floc_to_delay_accounting_events:
                floc_to_delay_accounting_events[floc] = []
            floc_to_delay_accounting_events[floc].append(delay_accounting_event)
        return floc_to_delay_accounting_events


class AnnotatedJSONDataset:

    """
    A class that represents an annotated JSON dataset, i.e. a dataset that has been annotated via Redcoat and saved in JSON format.

    Attributes:
        documents (List): A list of Document objects in this dataset.
        entity_classes (Dictionary): A dictionary of entity classes.
    """

    def __init__(self, data_file, csv_file, hierarchy, ignored_base_classes):
        self.entity_classes = self.get_entity_classes(hierarchy.entity_classes)
        self.documents = self.read_dataset(
            data_file, csv_file, hierarchy, ignored_base_classes
        )

    def get_entity_classes(self, hierarchy):
        entity_class_mapping = {h.name: i for i, h in enumerate(hierarchy)}
        return entity_class_mapping

    def read_dataset(
        self, data_file, csv_file, hierarchy, ignored_base_classes
    ):
        def cast_value(value, field):
            if field == "Work_Order_Functional_Location":
                return str(value)
            if value.isnumeric():
                return int(value)
            else:
                return str(value)

        print(csv_file, data_file)

        csv_rows = []
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                structured_fields = {
                    field.strip().replace(" ", "_"): cast_value(
                        row[field], field
                    )
                    for field in row
                    if len(field) > 1
                }
                csv_rows.append(structured_fields)

        documents = []
        with jsonlines.open(data_file, "r") as f:
            i = 0
            for line in f:
                i += 1

                # if i > 1000:
                #   break

                tokens = line["tokens"]

                csv_row = csv_rows[line["doc_idx"]]

                mentions = line["mentions"]

                d = Document(index=i, tokens=tokens, structured_fields=csv_row)

                for m in mentions:
                    if any([x in ignored_base_classes for x in m["labels"]]):
                        continue
                    mention_obj = Mention(
                        start=m["start"],
                        end=m["end"],
                        labels=[
                            hierarchy.entity_classes[self.entity_classes[l]]
                            for l in m["labels"]
                        ],
                        text=" ".join(tokens[m["start"] : m["end"]]),
                    )
                    d.add_mention(mention_obj)

                # d = Document(index = i, tokens = nltk.word_tokenize(doc.lower().strip()), structured_fields = structured_fields)

                documents.append(d)

        return documents


class MaintenanceGraphBuilder:

    """
    Maintenance graph builder takes a dataset as input and constructs a Neo4J graph via py2neo.

    Attributes:
        dataset (AnnotatedJSONDataset): An AnnotatedJSONDataset.
        defined_fields (dict): A dictionary of defined structured fields.
        graph (Graph): The Neo4J graph that will be populated.
        hierarchy (Hierarchy): A Hierarchy object storing the category hierarchy.
        node_normaliser (LexicalNormaliser): A LexicalNormaliser whose purpose is to clean the nodes, resolving issues such as making 'leaks', 'leaking' etc resolve to a single 'leak' node.
            delay_accounting_dataset (Delay AccountingDataset): An Delay AccountingDataset.
    """

    def __init__(
        self,
        dataset,
        hierarchy,
        node_normaliser=None,
        defined_fields=None,
        delay_accounting_dataset=None,
    ):
        """Summary

        Args:
            dataset (AnnotatedJSONDataset): An AnnotatedJSONDataset.
            hierarchy (Hierarchy): A Hierarchy object storing the category hierarchy.
            node_normaliser (LexicalNormaliser): A LexicalNormaliser whose purpose is to clean the nodes, resolving issues such as making 'leaks', 'leaking' etc resolve to a single 'leak' node.
            defined_fields (dict): A dictionary of defined structured fields.
        """
        self.dataset = dataset
        self.delay_accounting_dataset = delay_accounting_dataset
        self.hierarchy = hierarchy
        self.graph = Graph(password=env("GRAPH_PASSWORD"))
        self.node_normaliser = node_normaliser
        self.defined_fields = defined_fields

    def add_delay_accounting_events(
        self, document, floc_node, relationships, delay_accounting_id_set
    ):  # Incorporate Delay Accounting Data

        floc = document.structured_fields["Work_Order_Functional_Location"]

        # Check whether the FLOC of this document is present in the floc_to_delay_accounting_events mapping, i.e.
        # the FLOC appears in the Delay Accounting dataset.
        # If it does, create an Delay Accounting Event node for each Delay Accounting Event with the same FLOC.
        if floc in self.delay_accounting_dataset.floc_to_delay_accounting_events:
            delay_accounting_events = self.delay_accounting_dataset.floc_to_delay_accounting_events[floc]
            print(floc, delay_accounting_events)

            for delay_accounting_event in delay_accounting_events:
                delay_accounting_id = delay_accounting_event["Downtime ID"]
                # Only create a node for this Delay Accounting Event if it has not already been seen.
                if delay_accounting_id not in delay_accounting_id_set:
                    delay_accounting_id_set.add(delay_accounting_id)

                    floc_desc = document.structured_fields[
                        "Functional_Location_Description"
                    ]

                    delay_accounting_node = Node(
                        "Delay Accounting_Event",
                        name=delay_accounting_event["EXPLANATION"],
                        floc_desc=floc_desc,
                        effective_duration=delay_accounting_event["EFF_DURATION"],
                        lost_feed=delay_accounting_event["Nickel Tonnes"],
                    )

                    self.tx.create(delay_accounting_node)

                    # Add a relationship between the Item and Delay Accounting_Event if it does not already exist.
                    if delay_accounting_node not in relationships:
                        relationships[delay_accounting_node] = {}
                    if floc_node not in relationships[delay_accounting_node]:
                        relationships[delay_accounting_node][floc_node] = {
                            "HAS_Delay Accounting_EVENT": 1
                        }

    # Split the FLOC into components
    def split_floc(self, floc):
        return str(floc).replace(".", "-").split("-")

    # Transform a list of floc components (e.g. ['20', '3', 'PUU04']) into a list of components
    def get_floc_node_ids(self, _split_floc):
        floc_node_ids = []
        for i in range(1, len(_split_floc) + 1):
            floc_node_id = ""
            for x in _split_floc[0:i]:
                if len(floc_node_id) > 0:
                    floc_node_id += "-"  # if x[0].isnumeric() else '-'
                floc_node_id += x

            floc_node_ids.append(str(floc_node_id))
        return floc_node_ids

    def build_graph(self):
        """
        Constructs the graph.
        # TODO: Clean this entire function up.
        """
        self.graph.delete_all()
        self.tx = self.graph.begin()
        tx = self.tx

        entity_nodes = {}
        entity_objects = {}
        item_sets = []
        item_names_set = set()

        instance_nodes = {}
        instance_item_sets = []

        floc_dict = {}

        relationships = {}  # node_1 -> node_2 -> type -> freq

        seen_docs = set()

        floc_sort_field_names = {}
        print("Constructing FLOC nodes...")
        for doc_idx, document in enumerate(self.dataset.documents):

            floc = document.structured_fields[
                "Work_Order_Functional_Location"
            ].replace(".", "-")
            split_floc = self.split_floc(floc)
            floc_node_ids = self.get_floc_node_ids(split_floc)

            floc_sort_field_names[floc] = document.structured_fields[
                "Functional_Location_Sort_Field"
            ]  # .replace('.', '-')

            print(floc, ">", floc_sort_field_names[floc])
            print(floc_node_ids)

            for i, floc_node_id in enumerate(floc_node_ids[:-1]):
                if floc_node_id not in floc_dict:
                    floc_dict[floc_node_id] = {}

                if i > 0:
                    floc_dict[floc_node_id]["parent"] = floc_node_ids[i - 1]
                    floc_dict[floc_node_id]["parent_tree"] = [
                        ("FLOC/" + flid.replace("-", ".").replace(".", "/"))
                        for flid in floc_node_ids[:i]
                    ]

            if len(floc_node_ids) > 1:
                floc_dict[floc_node_ids[-1]] = {
                    "parent": floc_node_ids[-2],
                    "parent_tree": [
                        ("FLOC/" + flid.replace("-", ".").replace(".", "/"))
                        for flid in floc_node_ids
                    ],
                }
            else:
                floc_dict[floc_node_ids[0]] = {}

            # print(floc_node_ids[0], floc_dict[floc_node_ids[0]])

        for k, v in floc_sort_field_names.items():
            # print(k, ">", v)
            print(k)
            print("---")
            floc_dict[str(k)]["sort_field_name"] = v

            # print(k, v)

        floc_nodes = {}
        for k, v in floc_dict.items():
            parent_tree = v["parent_tree"] if "parent_tree" in v else []
            sf_name = v["sort_field_name"] if "sort_field_name" in v else ""
            # print(sf_name, k, "XX")

            n = Node(
                "Instance", "FLOC", *parent_tree, name=k, sort_field_name=k
            )  # sf_name

            floc_nodes[k] = n
            tx.create(n)

        for k, v in floc_dict.items():
            if "parent" not in v:
                continue
            node_id = floc_nodes[k]
            parent_node_id = floc_nodes[v["parent"]]

            if parent_node_id not in relationships:
                relationships[parent_node_id] = {}
            relationships[parent_node_id][node_id] = {"SCO": 1}

        print(relationships)
        print("Constructing entity nodes...")

        base_entity_node = Node("Entity", name="Entity")
        tx.create(base_entity_node)
        for entity in self.hierarchy.entity_classes:
            # print(entity)
            e = Node("Entity", entity.base_class, name=entity.name)
            tx.create(e)
            entity_nodes[id(entity)] = e
            entity_objects[id(entity)] = entity

            if entity.parent is not None:
                parent_id = id(entity.parent)
                if parent_id in entity_nodes:
                    p = entity_nodes[parent_id]
                else:
                    p = Node("Entity", name=entity.parent.name)
                    tx.create(p)
            else:
                p = base_entity_node
            ep = Relationship(e, "SCO", p)
            tx.create(ep)

        mention_relation_types = {}

        delay_accounting_id_set = set()

        defined_fields_dict = {d["name"]: d for d in self.defined_fields}

        for doc_idx, document in enumerate(self.dataset.documents):

            # doc_str = " ".join(document.tokens).replace(",", " ")
            # if doc_str in seen_docs:
            #   continue
            # seen_docs.add(doc_str) # Ignore duplicate documents

            print(
                "Document %d" % doc_idx,
                "of",
                "%d" % len(self.dataset.documents),
            )
            structured_fields = document.structured_fields
            final_structured_fields = {}
            for f in structured_fields:
                if f in defined_fields_dict:
                    if defined_fields_dict[f]["type"] == "Date":

                        try:
                            d = parse_date(structured_fields[f])
                        except:
                            d = structured_fields[f]

                        neo_date = neotime.Date(d.year, d.month, d.day)
                        structured_fields[f] = neo_date

                        # neo_date = neotime.DateTime.now().to_native()
                        # n = neo_date

                        # print(n)

                    if defined_fields_dict[f]["type"] == "Integer":
                        structured_fields[f] = int(float(structured_fields[f]))

                    final_structured_fields[f] = structured_fields[f]

            final_structured_fields[
                "Work_Order_Functional_Location"
            ] = document.structured_fields["Work_Order_Functional_Location"]

            if (
                "Order" in document.structured_fields
                and "Notification" in document.structured_fields
            ):
                final_structured_fields["Order"] = document.structured_fields[
                    "Order"
                ]
                final_structured_fields[
                    "Notification"
                ] = document.structured_fields["Notification"]

            # if "feluwa" in document.tokens and "shaft" in document.tokens:
            #   print(" ".join(document.tokens), final_structured_fields)

            d = Node(
                "Document",
                doc_id=document.index,
                tokens=" ".join(document.tokens).replace(",", " "),
                **final_structured_fields
            )

            floc_node = floc_nodes[
                str(
                    document.structured_fields[
                        "Work_Order_Functional_Location"
                    ]
                ).replace(".", "-")
            ]
            df = Relationship(floc_node, "APPEARS_IN", d)
            tx.create(df)

            item_set = set()
            instance_item_set = set()
            item_nodes = []
            non_item_nodes = []

            # For each mention in the document, construct a node.
            for mention in document.mentions:

                entity = mention.labels[0]
                # Remove any labels that are not the same bass class as this label
                # if "Item" in [m.name for m in mention.labels]:
                # if entity.base_class == "Cardinality":
                #   print([x.name for x in mention.labels])
                final_labels = []
                for i, l in enumerate(mention.labels):

                    if l.base_class == entity.base_class:
                        final_labels.append(l)

                entity_label = entity.name

                if "/" in entity_label:
                    continue

                if entity.base_class not in instance_nodes:
                    instance_nodes[entity.base_class] = {}

                instance_text = mention.text
                if self.node_normaliser is not None:
                    instance_text = self.node_normaliser.normalise_text(
                        instance_text
                    )

                if instance_text not in instance_nodes[entity.base_class]:
                    labels = final_labels

                    m = Node(
                        "Instance",
                        *[entity.name for entity in final_labels],
                        name=instance_text
                    )
                    instance_nodes[entity.base_class][instance_text] = m
                    tx.create(m)

                m = instance_nodes[entity.base_class][instance_text]
                me = Relationship(m, "INSTANCE_OF", entity_nodes[id(entity)])
                tx.create(me)
                if entity_label == "Item":
                    item_nodes.append(m)
                    item_names_set.add(instance_text)
                else:
                    non_item_nodes.append((m, entity.base_class))

                dm = Relationship(m, "APPEARS_IN", d)
                tx.create(dm)
                item_set.add(id(entity))
                instance_item_set.add(instance_text)

            # For each item in the list of nodes that are Items, they must be linked to every other Item in the work order.
            for i, item_node in enumerate(item_nodes):

                for other_item_node in item_nodes[i + 1 :]:

                    # Sort them to prevent issues with directed acyclic graph not loading properly
                    # It's very annoying that neo4j doesn't support undirected relationships, or else this wouldn't be necessary
                    item_1, item_2 = sorted(
                        [item_node, other_item_node],
                        key=lambda x: (str(x.labels) + str(dict(x)["name"])),
                    )

                    # print(item_1, item_2)
                    if item_1 not in relationships:
                        relationships[item_1] = {}

                    if item_2 not in relationships[item_1]:
                        relationships[item_1][item_2] = {}

                    if "APPEARS_WITH" not in relationships[item_1][item_2]:
                        relationships[item_1][item_2]["APPEARS_WITH"] = 0
                    relationships[item_1][item_2]["APPEARS_WITH"] += 1
                    # ii = Relationship(item_node, "APPEARS_WITH", other_item_node)
                    # tx.create(ii)

            # For every non item node, they must be linked to every Item node in the work order.
            for (non_item_node, base_class) in non_item_nodes:
                if non_item_node not in relationships:
                    relationships[non_item_node] = {}

                for item_node in item_nodes:

                    r = "HAS_%s" % base_class.upper()

                    if item_node not in relationships[non_item_node]:
                        relationships[non_item_node][item_node] = {}
                    if r not in relationships[non_item_node][item_node]:
                        relationships[non_item_node][item_node][r] = 0
                    relationships[non_item_node][item_node][r] += 1

                r = "HAS_%s" % base_class.upper()
                if floc_node not in relationships[non_item_node]:
                    relationships[non_item_node][floc_node] = {}
                if r not in relationships[non_item_node][floc_node]:
                    relationships[non_item_node][floc_node][r] = 0
                relationships[non_item_node][floc_node][r] += 1

            item_sets.append(item_set)
            instance_item_sets.append(instance_item_set)

            if self.delay_accounting_dataset:
                self.add_delay_accounting_events(
                    document, floc_node, relationships, delay_accounting_id_set
                )

                # print("XXXXXXXXXXXXXXXXXXXXXX", relationships[item_node][delay_accounting_node])
                # exit()

                # if "APPEARS_WITH" not in relationships[item_1][item_2]:
                #   relationships[item_1][item_2]["APPEARS_WITH"] = 0
                # relationships[item_1][item_2]["APPEARS_WITH"] += 1

        print("Building relationships")
        # Construct all of the relationships via Py2neo.
        for node_idx, node in enumerate(relationships):
            print("Relationship %d of %d" % (node_idx, len(relationships)))
            for other_node in relationships[node]:
                for relationship_type in relationships[node][other_node]:
                    freq = relationships[node][other_node][relationship_type]
                    ii = Relationship(
                        other_node, relationship_type, node, frequency=freq
                    )
                    tx.create(ii)

        # Originally this function also created Association Rule Object nodes (representing Association Rules in the data), but this has been
        # removed for now.

        # create_association_rule_nodes(item_sets, entity_objects, tx, entity_nodes)

        tx.commit()

        # with open('item_names.txt', 'w') as f:
        #   f.write("\n".join(sorted(list(item_names_set))))

    def save_metadata(self, filename, documents_name):
        """
        Save metadata about the graph to a json file.

        Args:
            filename (string): The name of the file in which the metadata will be saved.
            documents_name (stirng): The name of te document nodes, e.g. "Work orders", "Accident reports", etc.

        Returns:
            TYPE: Description
        """
        defined_fields = self.defined_fields

        for i, f in enumerate(defined_fields):
            if f["type"] == "Integer":
                defined_fields[i]["min"] = None
                defined_fields[i]["max"] = None
            elif f["type"] == "Date":
                defined_fields[i]["earliest"] = None
                defined_fields[i]["latest"] = None
            if f["type"] == "Categorical":
                defined_fields[i]["options"] = set()

        for d in self.dataset.documents:
            for i, f in enumerate(defined_fields):
                v = d.structured_fields[f["name"]]

                field_type = f["type"]
                if field_type == "Integer":

                    if type(v) is str and "." in v:
                        v = int(v.split(".")[0])
                        if v < 0:
                            v = 0
                    if type(v) is str and v[0] == "-":
                        v = 0
                    # print(f['min'], type(f['min']), v, type(v))

                    if f["min"] is None or v < f["min"]:
                        defined_fields[i]["min"] = v
                    if f["max"] is None or v > f["max"]:
                        defined_fields[i]["max"] = v

                if field_type == "Date":
                    date = v
                    print(
                        v, f["earliest"], f["latest"]
                    )  # TODO: Fix this up - there was an issue with date parsing and I
                    # added this 'str' check as a way to bypass the issue. For some reason dates are being passed here as strings
                    # occasionally
                    if type(date) is not str:
                        if f["earliest"] is None or date < f["earliest"]:
                            defined_fields[i]["earliest"] = v
                        if f["latest"] is None or date > f["latest"]:
                            defined_fields[i]["latest"] = v

                elif field_type == "Categorical":
                    if v not in f["options"]:
                        defined_fields[i]["options"].add(v)

        for i, f in enumerate(defined_fields):
            if f["type"] == "Categorical":
                defined_fields[i]["options"] = sorted(list(f["options"]))
            if f["type"] == "Date":
                for x in ["earliest", "latest"]:
                    defined_fields[i][x] = "%s/%s/%s" % (
                        f[x].day,
                        f[x].month,
                        f[x].year,
                    )

        with open(filename, "w") as f:
            json.dump(
                {
                    "structured_fields": defined_fields,
                    "documents_name": documents_name,
                },
                f,
            )
        return


def main(
    data_file,
    csv_file,
    hierarchy_file,
    defined_fields,
    documents_name="Document",
    delay_accounting_data_file=None,
):

    ignored_base_classes = set(["Unsure"])

    hierarchy = Hierarchy(hierarchy_file)

    dataset = AnnotatedJSONDataset(
        data_file, csv_file, hierarchy, ignored_base_classes
    )

    if delay_accounting_data_file:
        delay_accounting_dataset = Delay AccountingDataset(delay_accounting_data_file)
    else:
        delay_accounting_dataset = None

    node_normaliser = LexicalNormaliser()
    graph_builder = MaintenanceGraphBuilder(
        dataset, hierarchy, node_normaliser, defined_fields, delay_accounting_dataset
    )

    graph_builder.build_graph()
    graph_builder.save_metadata(
        os.path.join(
            CURRENT_PATH.parent.parent, "echidna_app/data/metadata.json"
        ),
        documents_name,
    )


def build_triples(
    ner_input_filename,
    mwo_input_filename,
    entity_hierarchy_input_filename,
    delay_accounting_data_filename=None,
):
    main(
        data_file=ner_input_filename,
        csv_file=mwo_input_filename,
        defined_fields=[
            {"name": "Work_Order_Basic_Start_Date", "type": "Date"},
            {"name": "Work_Order_Total_Actual_Cost", "type": "Integer"},
            {"name": "Functional_Location_Description", "type": "Categorical"},
            {"name": "Functional_Location_Sort_Field", "type": "Categorical"},
            {"name": "Work_Order_Type", "type": "Categorical"},
        ],
        hierarchy_file=entity_hierarchy_input_filename,
        documents_name="Work order",
        delay_accounting_data_file=delay_accounting_data_filename,
    )


if __name__ == "__main__":
    # main(data_file = 'input/dmp_data.csv',
    #    max_lines = 5000,
    #    hierarchy_file = 'input/categories.txt'
    #   )

    pass

    # config = configparser.ConfigParser()
    # config.read('../config.ini')

    # main_grammar(data_file = 'input/agreed_data_joined.json',
    #                hierarchy_file = 'input/categories_mwos.txt')
