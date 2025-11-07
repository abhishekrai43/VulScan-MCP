import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import logging
import re
log = logging.getLogger("vulscan-mcp")

def parse_manifest(manifest_path: str) -> List[Dict[str, str]]:
    """Parse a manifest file and return a list of dependencies with name and version."""
    try:
        if manifest_path.endswith("package.json"):
            with open(manifest_path, encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            deps = data.get("dependencies", {})
            return [{"name": k, "version": v} for k, v in deps.items()]
        
        if manifest_path.endswith("requirements.txt"):
            deps = []
            with open(manifest_path, encoding='utf-8', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if "==" in line:
                        name, version = line.split("==", 1)
                        deps.append({"name": name.strip(), "version": version.strip()})
            return deps
        
        if manifest_path.endswith("pyproject.toml"):
            # Minimal TOML parsing for poetry
            deps = []
            with open(manifest_path, encoding='utf-8', errors='replace') as f:
                in_deps_section = False
                for line in f:
                    if line.strip().startswith("[tool.poetry.dependencies]"):
                        in_deps_section = True
                        continue
                    if in_deps_section and line.strip().startswith("["):
                        break
                    if in_deps_section and "=" in line and not line.strip().startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            name, version = parts
                            deps.append({"name": name.strip(), "version": version.strip().strip('"')})
            return deps
        
        if manifest_path.endswith("pom.xml"):
            with open(manifest_path, encoding='utf-8', errors='replace') as f:
                tree = ET.parse(f)
            root = tree.getroot()
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
            deps = []
            for dep in root.findall('.//m:dependency', ns):
                name_elem = dep.find('m:artifactId', ns)
                version_elem = dep.find('m:version', ns)
                if name_elem is not None and name_elem.text:
                    deps.append({
                        "name": name_elem.text,
                        "version": version_elem.text if version_elem is not None else ""
                    })
            return deps
        
        if manifest_path.endswith("build.gradle") or manifest_path.endswith("build.gradle.kts"):
            # Parse Gradle build files for dependencies
            deps = []
            with open(manifest_path, encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Look for dependency declarations in various Gradle formats
            # implementation 'group:name:version'
            # compile 'group:name:version'  
            # api 'group:name:version'
            # runtimeOnly 'group:name:version'
            # testImplementation 'group:name:version'
            
            patterns = [
                r"(?:implementation|compile|api|runtimeOnly|testImplementation|testCompile)\s+['\"]([^:]+):([^:]+):([^'\"]+)['\"]",
                r"(?:implementation|compile|api|runtimeOnly|testImplementation|testCompile)\s*\(\s*['\"]([^:]+):([^:]+):([^'\"]+)['\"]\s*\)",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for group, name, version in matches:
                    # For Gradle, we typically care about the artifact name, not the full group:name
                    deps.append({
                        "name": name,
                        "version": version
                    })
            
            return deps
        
        # Add more formats as needed
        return []
    
    except Exception as e:
        log.error(f"Failed to parse manifest {manifest_path}: {e}")
        return []
