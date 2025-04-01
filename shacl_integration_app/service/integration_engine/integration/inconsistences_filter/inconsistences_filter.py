from shacl_integration_app.repository.models import Cluster, ConceptCluster, NodeAxiomCluster, PropertyCluster
from shacl_integration_app.repository.rule_library.filter_library import Filter_Library
import shacl_integration_app.service.rule_engine as rule_engine
from rdflib import Graph, URIRef, RDF, Literal
import uuid

class InconsistencesFilter:
    """
    Class to filter inconsistencies in the SHACL integration process.
    """
    def __init__(self, concept_clusters: list[Cluster], inconsistences_report_path: str, integration_option: str) -> None:
        self.concept_clusters: list[Cluster] = concept_clusters
        self.final_clusters: list[Cluster] = []
        self.integration_option: str = integration_option
        self.inconsistences_report_path: str = inconsistences_report_path
        self.inconsistences_graph: Graph = Graph()
        # PREFIXES
        self.inconsistences_graph.bind('sh', 'http://www.w3.org/ns/shacl#')
        self.inconsistences_graph.bind('inc', 'http://www.inconsistence.es#')
        self.inconsistences_graph.bind('inc-ex', 'http://www.inconsistence_example.es/resource/')


    def filter_inconsistencies(self) -> list[Cluster]:
        """
        Filter inconsistencies from the SHACL data.
        """

        for cluster in self.concept_clusters:
            node_result: list[bool] = self.filter_node_inconsistences(list_node=cluster.node_axiom_cluster_list, cluster_concept=cluster.concept_list)
            property_result: list[bool] = [self.filter_property_inconsistences(prop=prop, cluster_concept=cluster.concept_list) for prop in cluster.property_cluster_list]
            if True not in node_result and True not in property_result:
                self.final_clusters.append(cluster)

        self.inconsistences_graph.serialize(destination=self.inconsistences_report_path, format='turtle')

        return self.final_clusters
    
    def filter_node_inconsistences(self, list_node: list[NodeAxiomCluster], cluster_concept: list[str]) -> bool:
        """
        Filter inconsistencies from the node axioms.
        """
        list_inconsistencies: list[bool] = []

        # print(f'Node: {list_node}')
        # print('\n')

        filter_dict: list[dict] = [
            {
                'filter' : ['http://www.w3.org/ns/shacl#nodeKind'],
                'list' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#closed'],
                'list' : []
            }
        ]
        for node in list_node:
            [filter_dict[filter_dict.index(fil)]['list'].append(node) for fil in filter_dict if node.concept in fil['filter']]

        
        list_inconsistencies = [self.execute_filter_node(filter=fil, cluster_concept=cluster_concept) for fil in filter_dict]
          
        return list_inconsistencies
        

    def filter_property_inconsistences(self, prop: PropertyCluster, cluster_concept: list[str]) -> bool:
        """
        Filter inconsistencies from the property axioms.
        ::return: False if there is no inconsistency, True if there is an inconsistency.
        """

        list_inconsistencies: list[bool] = []

        filter_dict: list[dict] = [
            {
                'filter' : ['http://www.w3.org/ns/shacl#equals', 'http://www.w3.org/ns/shacl#disjoint'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minCount', 'http://www.w3.org/ns/shacl#maxCount'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minExclusive', 'http://www.w3.org/ns/shacl#maxExclusive', 'http://www.w3.org/ns/shacl#minInclusive', 'http://www.w3.org/ns/shacl#maxInclusive'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#minLength', 'http://www.w3.org/ns/shacl#maxLength'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#qualifiedMinCount', 'http://www.w3.org/ns/shacl#qualifiedMaxCount'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#uniqueLang', 'http://www.w3.org/ns/shacl#languageIn'],
                'list' : [],
                'path' : []
            },
            {
                'filter' : ['http://www.w3.org/ns/shacl#in'],
                'list' : [],
                'path' : []
            }
        ]

        for axiom in prop.property_axiom_cluster_list:
            for ax in axiom['axioms']:
                [(filter_dict[filter_dict.index(fil)]['path'].append(axiom['path']), filter_dict[filter_dict.index(fil)]['list'].append(ax)) for fil in filter_dict if ax['predicate'] in fil['filter']]

        list_inconsistencies = [self.execute_filter_property(filter=fil, cluster_concept=cluster_concept) for fil in filter_dict]
        # print(f'Filter dict: {filter_dict}')

        # print('Property:', prop)
        
        return list_inconsistencies


    def execute_filter_property(self, filter: dict[str|list[str]], cluster_concept: list[str]) -> bool:
        filter_result: bool = False
        axiom_list: list[str] = []
        lo_list: list[str] = []
        filter_library = Filter_Library()
        axiom_list = list(set(axiom_list))

        if len(axiom_list) == 1:
            filter_result = False
            return filter_result
        
        if 'http://www.w3.org/ns/shacl#nodeKind' in filter['filter'] and len(filter['list']) > 0:
            path_list: list[str] = []
            for path in filter['path']:
                if path not in path_list:
                    path_list.append(path)
            for axiom in filter['list']:
                for a1 in axiom['objects']:
                    for a2 in axiom['objects']:
                        if a1 != a2:
                            fact: rule_engine.Fact = rule_engine.Fact(nodeKind1=a1, nodeKind2=a2)
                            if self.integration_option == 'intersection':
                                filter_result = filter_library.rule_multiple.evaluate_multiple_rules_with_result([fact], filter_library.nodeKindIntersectionFilter)
                                if True in filter_result:
                                    dict_response = {
                                        'filter': cluster_concept,
                                        'axioms': [a1, a2],
                                        'path': path,
                                        'inconsistency': 'sh:nodeKind not compatible'
                                    }
                                    self.generate_inconsistences_report(dict_response=dict_response)
                                    return True
                            elif self.integration_option == 'union':
                                filter_result = filter_library.rule_multiple.evaluate_multiple_rules_with_result([fact], filter_library.nodeKindUnionFilter)
                                if True in filter_result:
                                    dict_response = {
                                        'filter': cluster_concept,
                                        'axioms': [a1, a2],
                                        'path': path,
                                        'inconsistency': 'sh:nodeKind not compatible.'
                                    }
                                    self.generate_inconsistences_report(dict_response=dict_response)
                                    return True

        if self.integration_option == 'intersection':
            path_list: list[str] = []
            for path in filter['path']:
                if path not in path_list:
                    path_list.append(path)
            if 'http://www.w3.org/ns/shacl#closed' in filter['filter'] and len(filter['list']) > 0:
                for axiom in filter['list']:
                    for a1 in axiom['objects']:
                        for a2 in axiom['objects']:
                            if a1 != a2:
                                fact: rule_engine.Fact = rule_engine.Fact(closed1=bool(a1), closed2=bool(a2))
                                filter_result = filter_library.closedFilter.evaluate_with_result([fact])
                                if True in filter_result:
                                    dict_response = {
                                        'filter': cluster_concept,
                                        'axioms': [a1, a2],
                                        'path': path,
                                        'inconsistency': 'sh:closed not compatible.'
                                    }
                                    self.generate_inconsistences_report(dict_response=dict_response)
                                    return filter_result
                                
            if 'http://www.w3.org/ns/shacl#equals' in filter['filter'] and len(filter['list']) > 0:
                path_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)
                        
                equals_list: list[str] = []
                disjoint_list: list[str] = []
                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#equals':
                        equals_list.extend(axiom['objects'])
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#disjoint':
                        disjoint_list.extend(axiom['objects'])
                if len(equals_list) == 0 or len(disjoint_list) == 0:
                    return False
                for a1 in equals_list:
                    for a2 in disjoint_list:
                        fact: rule_engine.Fact = rule_engine.Fact(equals=a1, disjoint=a2)
                        filter_result = filter_library.equalsDisjointFilter.evaluate_with_result([fact])
                        if True in filter_result:
                            dict_response = {
                                'filter': cluster_concept,
                                'axioms': [a1, a2],
                                'path': path,
                                'inconsistency': 'sh:equals and sh:disjoint not compatible.'
                            }
                            self.generate_inconsistences_report(dict_response=dict_response)
                            return filter_result
                    
            if 'http://www.w3.org/ns/shacl#minCount' in filter['filter'] and len(filter['list']) > 0:
                min_count_list: list[str] = []
                max_count_list: list[str] = []
                path_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)
                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#minCount':
                        min_count_list.extend(axiom['objects'])
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#maxCount':
                        max_count_list.extend(axiom['objects'])
                if len(min_count_list) == 0 or len(max_count_list) == 0:
                    return False
                fact: rule_engine.Fact = rule_engine.Fact(minCount=max(min_count_list), maxCount=min(max_count_list))
                filter_result = filter_library.countFilter.evaluate_with_result([fact])
                if True in filter_result:
                    dict_response = {
                        'filter': cluster_concept,
                        'axioms': ['http://www.w3.org/ns/shacl#minCount', 'http://www.w3.org/ns/shacl#maxCount'],
                        'path': path,
                        'inconsistency': 'sh:minCount greater or equals than sh:maxCount.'
                    }
                    self.generate_inconsistences_report(dict_response=dict_response)
                    return filter_result
            
            if 'http://www.w3.org/ns/shacl#minExclusive' in filter['filter'] and len(filter['list']) > 0:
                min_exclusive_list: list[str] = []
                min_exclusive_value: str = None
                max_exclusive_list: list[str] = []
                max_exclusive_value: str = None
                min_inclusive_list: list[str] = []
                min_inclusive_value: str = None
                max_inclusive_list: list[str] = []
                max_inclusive_value: str = None
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)
                        
                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#minInclusive':
                        min_inclusive_list.extend(axiom['objects'])
                        if len(min_inclusive_list) != 0:
                            min_inclusive_value = max(min_inclusive_list)
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#maxInclusive':
                        max_inclusive_list.extend(axiom['objects'])
                        if len(max_inclusive_list) != 0:
                            max_inclusive_value = min(max_inclusive_list)
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#minExclusive':
                        min_exclusive_list.extend(axiom['objects'])
                        if len(min_exclusive_list) != 0:
                            min_exclusive_value = max(min_exclusive_list)
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#maxExclusive':
                        max_exclusive_list.extend(axiom['objects'])
                        if len(max_exclusive_list) != 0:
                            max_exclusive_value = min(max_exclusive_list)

                fact2: rule_engine.Fact = rule_engine.Fact(minInclusive=min_inclusive_value, minExclusive=min_exclusive_value, maxInclusive=max_inclusive_value, maxExclusive=max_exclusive_value)
                filter_result = filter_library.rule_multiple.evaluate_multiple_rules_with_result([fact2], filter_library.evaluateInExClusiveFilter)
                if True in filter_result:
                    dict_response = {
                        'filter': cluster_concept,
                        'axioms': ['http://www.w3.org/ns/shacl#minInclusive', 'http://www.w3.org/ns/shacl#maxInclusive', 'http://www.w3.org/ns/shacl#minExclusive', 'http://www.w3.org/ns/shacl#maxExclusive'],
                        'path': path,
                        'inconsistency': 'Error within sh:minExclusive, sh:maxExclusive, sh:minInclusive and sh:maxInclusive.'
                    }
                    self.generate_inconsistences_report(dict_response=dict_response)
                    return True
                    
            if 'http://www.w3.org/ns/shacl#minLength' in filter['filter'] and len(filter['list']) > 0:
                min_length_list: list[str] = []
                max_length_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)

                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#minLength':
                        min_length_list.extend(axiom['objects'])
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#maxLength':
                        max_length_list.extend(axiom['objects'])

                if len(min_length_list) == 0 or len(max_length_list) == 0:
                    return False
                
                fact: rule_engine.Fact = rule_engine.Fact(minLength=max(min_length_list), maxLength=min(max_length_list))
                filter_result = filter_library.countFilter.evaluate_with_result([fact])
                if filter_result == True:
                    dict_response = {
                        'filter': cluster_concept,
                        'axioms': ['http://www.w3.org/ns/shacl#minLength', 'http://www.w3.org/ns/shacl#maxLength'],
                        'path': path,
                        'inconsistency': 'sh:minLength greater or equals than sh:maxLength.'
                    }
                    self.generate_inconsistences_report(dict_response=dict_response)
                    return filter_result
                    
            if 'http://www.w3.org/ns/shacl#qualifiedMinCount' in filter['filter'] and len(filter['list']) > 0:
                qualified_min_count_list: list[str] = []
                qualified_max_count_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)

                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#qualifiedMinCount':
                        qualified_min_count_list.extend(axiom['objects'])
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#qualifiedMaxCount':
                        qualified_max_count_list.extend(axiom['objects'])

                if len(qualified_min_count_list) == 0 or len(qualified_max_count_list) == 0:
                    return False
                fact: rule_engine.Fact = rule_engine.Fact(minCount=max(qualified_min_count_list), maxCount=min(qualified_max_count_list))
                filter_result = filter_library.countFilter.evaluate_with_result([fact])
                if filter_result == True:
                    dict_response = {
                        'filter': cluster_concept,
                        'axioms': ['http://www.w3.org/ns/shacl#qualifiedMinCount', 'http://www.w3.org/ns/shacl#qualifiedMaxCount'],
                        'path': path,
                        'inconsistency': 'sh:qualifiedMinCount greater or equals than sh:qualifiedMaxCount.'
                    }
                    self.generate_inconsistences_report(dict_response=dict_response)
                    return filter_result

            if 'http://www.w3.org/ns/shacl#uniqueLang' in filter['filter'] and len(filter['list']) > 0:
                unique_lang_list: list[str] = []
                language_in_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)

                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#uniqueLang':
                        unique_lang_list.extend(axiom['objects'])
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#languageIn':
                        language_in_list.extend(axiom['objects'])

                if len(unique_lang_list) == 0:
                    return False
                if len(unique_lang_list) > 0:
                    for lang1 in unique_lang_list:
                        for lang2 in language_in_list:
                            if lang1 != lang2:
                                dict_response = {
                                    'filter': cluster_concept,
                                    'axioms': ['http://www.w3.org/ns/shacl#uniqueLang'],
                                    'path': path,
                                    'inconsistency': 'sh:uniqueLang not compatible.'
                                }
                                self.generate_inconsistences_report(dict_response=dict_response)
                                return True
                if len(language_in_list) == 0:
                    return False
                
                if len(language_in_list) > 0:
                    for unique_lang in unique_lang_list:
                        for lang in language_in_list:
                            if unique_lang == True and len(lang) > 1:
                                dict_response = {
                                    'filter': cluster_concept,
                                    'axioms': ['http://www.w3.org/ns/shacl#uniqueLang', 'http://www.w3.org/ns/shacl#languageIn'],
                                    'path': path,
                                    'inconsistency': 'sh:uniqueLang and sh:languageIn not compatible.'
                                }
                                self.generate_inconsistences_report(dict_response=dict_response)
                                return True
                
            if 'http://www.w3.org/ns/shacl#in' in filter['filter'] and len(filter['list']) > 0:
                in_list: list[str] = []
                for path in filter['path']:
                    if path not in path_list:
                        path_list.append(path)

                for axiom in filter['list']:
                    if axiom['predicate'] == 'http://www.w3.org/ns/shacl#in':
                        in_list.extend(axiom['objects'])

                if len(in_list) == 0:
                    return False
                for a1 in in_list:
                    for a2 in in_list:
                        fact: rule_engine.Fact = rule_engine.Fact(in1=a1, in2=a2)
                        filter_result = filter_library.inFilter.evaluate_with_result([fact])
                        dict_response = {
                            'filter': cluster_concept,
                            'axioms': ['http://www.w3.org/ns/shacl#in'],
                            'path': path,
                            'inconsistency': 'sh:in not compatible.'
                        }
                        self.generate_inconsistences_report(dict_response=dict_response)
                        return True

        return False


    def execute_filter_node(self, filter: dict[str|list[str]], cluster_concept: list[str]) -> bool:
        """
        Filter the inconsistencies from the SHACL data.
        """
        filter_result: bool = False
        axiom_list: list[str] = []
        lo_list: list[str] = []
        filter_library = Filter_Library()

        for fil in filter['list']:
            for axiom in fil.axiom_list:
                axiom_list.append(axiom['obj'])
                lo_list.append(axiom['logical_operator'])
        
        lo_list = list(set(lo_list))
        axiom_list = list(set(axiom_list))

        if len(lo_list) > 1 and self.integration_option == 'intersection':
            dict_response = {
                        'filter': cluster_concept,
                        'axioms': [f'http://www.w3.org/ns/shacl#{str(lo)}' for lo in lo_list if lo != None],
                        'inconsistency': 'Logical constraints not compatible for intersection operation.'
                    }
            self.generate_inconsistences_report(dict_response=dict_response)
            filter_result = True
            return filter_result
        
        if len(axiom_list) == 1:
            filter_result = False
            return filter_result

        
        if 'http://www.w3.org/ns/shacl#nodeKind' in filter['filter'] and len(filter['list']) > 0:
            for axiom1 in axiom_list:
                for axiom2 in axiom_list:
                    fact: rule_engine.Fact = rule_engine.Fact(nodeKind1=axiom1, nodeKind2=axiom2)
                    if self.integration_option == 'intersection':
                        filter_result = filter_library.rule_multiple.evaluate_multiple_rules_with_result([fact], filter_library.nodeKindIntersectionFilter)
                        if True in filter_result:
                            dict_response = {
                                'filter': cluster_concept,
                                'axioms': [axiom1, axiom2],
                                'inconsistency': 'sh:nodeKind not compatible'
                            }
                            self.generate_inconsistences_report(dict_response=dict_response)
                            return filter_result
                    elif self.integration_option == 'union':
                        filter_result = filter_library.rule_multiple.evaluate_multiple_rules_with_result([fact], filter_library.nodeKindUnionFilter)
                        if True in filter_result:
                            dict_response = {
                                'filter': cluster_concept,
                                'axioms': [axiom1, axiom2],
                                'inconsistency': 'sh:nodeKind not compatible.'
                            }
                            self.generate_inconsistences_report(dict_response=dict_response)
                            return True
                        
        if self.integration_option == 'intersection':
            if 'http://www.w3.org/ns/shacl#closed' in filter['filter'] and len(filter['list']) > 0:
                for axiom1 in axiom_list:
                    for axiom2 in axiom_list:
                        fact: rule_engine.Fact = rule_engine.Fact(closed1=bool(axiom1), closed2=bool(axiom2))
                        filter_result = filter_library.closedFilter.evaluate_with_result([fact])
                        if filter_result == True:
                            dict_response = {
                                'filter': cluster_concept,
                                'axioms': [axiom1, axiom2],
                                'inconsistency': 'sh:closed not compatible.'
                            }
                            self.generate_inconsistences_report(dict_response=dict_response)
                            return filter_result

        
        return filter_result


    def generate_inconsistences_report(self, dict_response: dict) -> str:
        """
        Generate the SHACL inconsistencies report.
        """

        identifier: str = str(uuid.uuid4())

        self.inconsistences_graph.add((URIRef('http://www.inconsistence_example.es/resource/' + identifier), RDF.type, URIRef('http://www.inconsistence.es#Inconsistency')))
        for elem in dict_response['filter']:
            self.inconsistences_graph.add((URIRef('http://www.inconsistence_example.es/resource/' + identifier), URIRef('http://www.inconsistence.es#hasInconsistencyInClass'), URIRef(elem)))

        for axiom in dict_response['axioms']:
            self.inconsistences_graph.add((URIRef('http://www.inconsistence_example.es/resource/' + identifier), URIRef('http://www.inconsistence.es#hasInconsistencyAxiom'), URIRef(axiom)))

        if 'path' in dict_response:
            for path in dict_response['path']:
                self.inconsistences_graph.add((URIRef('http://www.inconsistence_example.es/resource/' + identifier), URIRef('http://www.inconsistence.es#hasInconsistencyPath'), URIRef(path)))
        
        self.inconsistences_graph.add((URIRef('http://www.inconsistence_example.es/resource/' + identifier), URIRef('http://www.inconsistence.es#hasReport'), Literal(dict_response['inconsistency'])))

        return self.inconsistences_report_path