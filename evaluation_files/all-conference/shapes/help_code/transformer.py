import rdflib
import re
from urllib.parse import urlparse

def transform_astrea_shapes(turtle_text):
    """
    Transforma las URIs de Astrea y cambia el prefijo por defecto ':' por la última palabra del namespace.
    
    Args:
        turtle_text (str): Texto en formato Turtle con shapes de Astrea.
    
    Returns:
        str: Texto Turtle transformado.
    """
    try:
        # Crear grafo y parsearlo
        graph = rdflib.Graph()
        graph.parse(data=turtle_text, format="turtle")
        
        # Namespace para SHACL
        SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
        
        # Diccionario para mapear URIs de Astrea a nuevas URIs
        uri_mapping = {}
        
        # Buscar todos los PropertyShapes de Astrea
        for subject in graph.subjects(rdflib.RDF.type, SH.PropertyShape):
            subject_str = str(subject)
            
            # Verificar si es una URI de Astrea
            if "astrea.linkeddata.es/shapes#" in subject_str:
                # Buscar el sh:path de este PropertyShape
                path_objects = list(graph.objects(subject, SH.path))
                
                if path_objects:
                    path_uri = str(path_objects[0])
                    
                    # Extraer el nombre del path (después del # o último /)
                    if '#' in path_uri:
                        path_name = path_uri.split('#')[-1]
                    else:
                        path_name = path_uri.split('/')[-1]
                    
                    # Crear nueva URI con shape_int:
                    new_uri = f"shape_int:{path_name}"
                    uri_mapping[subject_str] = new_uri
        
        # Buscar todos los NodeShapes de Astrea
        for subject in graph.subjects(rdflib.RDF.type, SH.NodeShape):
            subject_str = str(subject)
            
            # Verificar si es una URI de Astrea
            if "astrea.linkeddata.es/shapes#" in subject_str:
                # Buscar el sh:targetClass de este NodeShape
                target_class_objects = list(graph.objects(subject, SH.targetClass))
                
                if target_class_objects:
                    target_class_uri = str(target_class_objects[0])
                    
                    # Extraer el nombre de la clase (después del # o último /)
                    if '#' in target_class_uri:
                        class_name = target_class_uri.split('#')[-1]
                    else:
                        class_name = target_class_uri.split('/')[-1]
                    
                    # Crear nueva URI con shape_int:
                    new_uri = f"shape_int:{class_name}"
                    uri_mapping[subject_str] = new_uri
                else:
                    # Si no tiene targetClass, usar el hash de la URI original
                    hash_id = subject_str.split('#')[-1]
                    new_uri = f"shape_int:{hash_id}"
                    uri_mapping[subject_str] = new_uri
        
        # Convertir el grafo a texto
        serialized = graph.serialize(format="turtle")
        
        # Buscar el namespace por defecto y extraer la última palabra
        namespace_match = re.search(r'@prefix\s+:\s+<([^>]+)>\s+\.', serialized)
        if namespace_match:
            namespace_uri = namespace_match.group(1)
            
            # Extraer la última palabra del namespace (antes del #)
            if '#' in namespace_uri:
                last_word = namespace_uri.split('#')[0].split('/')[-1]
            else:
                last_word = namespace_uri.rstrip('/').split('/')[-1]
            
            # Reemplazar el prefijo por defecto ':' por la nueva palabra
            new_prefix_declaration = f"@prefix {last_word}: <{namespace_uri}> ."
            serialized = re.sub(r'@prefix\s+:\s+<[^>]+>\s+\.', new_prefix_declaration, serialized)
            
            # Reemplazar todas las referencias que usan ':' por el nuevo prefijo
            serialized = re.sub(r'(\s|^|,|\(|\[):([A-Za-z][A-Za-z0-9_]*)', f'\\1{last_word}:\\2', serialized)
        
        # Aplicar las transformaciones de URI de Astrea
        result_text = serialized
        for old_uri, new_uri in uri_mapping.items():
            # Reemplazar tanto cuando aparece como sujeto como cuando aparece como objeto
            result_text = result_text.replace(f"<{old_uri}>", new_uri)
        
        # Agregar el prefijo shape_int al inicio si no existe
        if "shape_int:" not in result_text and uri_mapping:
            # Buscar donde insertar el prefijo (después de otros prefijos)
            prefix_pattern = r"(@prefix\s+[^:]+:\s+<[^>]+>\s+\.\s*\n)"
            matches = list(re.finditer(prefix_pattern, result_text))
            
            if matches:
                # Insertar después del último prefijo
                last_match = matches[-1]
                insert_pos = last_match.end()
                shape_int_prefix = "@prefix shape_int: <http://example.org/shape_int#> .\n"
                result_text = result_text[:insert_pos] + shape_int_prefix + result_text[insert_pos:]
            else:
                # Si no hay prefijos, agregar al inicio
                shape_int_prefix = "@prefix shape_int: <http://example.org/shape_int#> .\n\n"
                result_text = shape_int_prefix + result_text
        
        return result_text
        
    except Exception as e:
        return f"Error al procesar el SHACL: {e}"

def process_shacl_file(input_file, output_file=None):
    """
    Procesa un archivo SHACL y transforma las URIs de Astrea.
    
    Args:
        input_file (str): Ruta del archivo de entrada.
        output_file (str): Ruta del archivo de salida (opcional).
    
    Returns:
        str: Texto transformado.
    """
    try:
        # Leer el archivo
        with open(input_file, 'r', encoding='utf-8') as f:
            turtle_content = f.read()
        
        # Transformar el contenido
        transformed_content = transform_astrea_shapes(turtle_content)
        
        # Guardar el resultado si se especifica archivo de salida
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transformed_content)
            print(f"Archivo transformado guardado en: {output_file}")
        
        return transformed_content
        
    except FileNotFoundError:
        return f"Error: No se encontró el archivo {input_file}"
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

# Ejemplo de uso
def main():
    print("Transformando shapes de Astrea...")
    # Ejemplo con archivo
    result = process_shacl_file("c:/Users/salgo/Developer/tesis/shacl_integration/evaluation_files/sosa-ssn-saref/shapes/sosa-ssn-astrea-shapes.ttl", "c:/Users/salgo/Developer/tesis/shacl_integration/evaluation_files/sosa-ssn-saref/shapes/sosa-ssn-astrea-shapes-transformed.ttl")
    # print(result)

if __name__ == "__main__":
    main()
    