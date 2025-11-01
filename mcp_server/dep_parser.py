import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional
import logging
import re

# Try to import tomllib (Python 3.11+), fallback to tomli for older versions
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

log = logging.getLogger("vulscan-mcp")

def _parse_dependency_string(dep_str: str) -> Optional[Dict[str, str]]:
    """
    Parse PEP 621 dependency string like:
    - "requests>=2.28.0"
    - "django==4.2.0"
    - "flask~=2.0"
    - "numpy"
    Returns {"name": "requests", "version": "2.28.0"} or None
    """
    # Pattern: package_name followed by optional version specifier
    # Examples: requests>=2.28.0, django[extra]>=4.0, flask
    match = re.match(r'^([a-zA-Z0-9_-]+)(?:\[.*?\])?(?:([><=~!]+)(.+))?', dep_str.strip())
    
    if not match:
        return None
    
    name = match.group(1)
    operator = match.group(2)
    version = match.group(3)
    
    if not version:
        return {"name": name, "version": ""}  # No version specified
    
    # Clean up version: remove spaces, quotes, and extra operators
    version = version.strip().strip('"\'')
    
    return {"name": name, "version": version}

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
            """
            Proper pyproject.toml parser supporting multiple formats:
            - PEP 621: [project] dependencies = ["package>=1.0"]
            - Poetry: [tool.poetry.dependencies]
            - uv: [tool.uv.sources]
            """
            deps = []
            
            if tomllib is None:
                log.warning("tomllib/tomli not available, skipping pyproject.toml parsing")
                return deps
            
            try:
                with open(manifest_path, 'rb') as f:
                    data = tomllib.load(f)
                
                # Strategy 1: PEP 621 format - [project] dependencies
                if 'project' in data and 'dependencies' in data['project']:
                    for dep_str in data['project']['dependencies']:
                        # Parse "package>=1.0.0" or "package==1.0.0" format
                        parsed = _parse_dependency_string(dep_str)
                        if parsed:
                            deps.append(parsed)
                
                # Strategy 2: Poetry format - [tool.poetry.dependencies]
                if 'tool' in data and 'poetry' in data['tool'] and 'dependencies' in data['tool']['poetry']:
                    poetry_deps = data['tool']['poetry']['dependencies']
                    for name, value in poetry_deps.items():
                        if name == 'python':  # Skip Python version constraint
                            continue
                        
                        # Handle different Poetry formats:
                        # Simple: requests = "^2.28.0"
                        # Complex: requests = { version = "^2.28.0", extras = ["security"] }
                        if isinstance(value, str):
                            version = value.strip('^~>=<')  # Strip Poetry version operators
                            deps.append({"name": name, "version": version})
                        elif isinstance(value, dict) and 'version' in value:
                            version = value['version'].strip('^~>=<')
                            deps.append({"name": name, "version": version})
                
                # Strategy 3: uv format - [tool.uv.sources] or [project] dependencies
                # uv uses PEP 621 format, already handled above
                
                return deps
                
            except Exception as e:
                log.error(f"Failed to parse pyproject.toml with tomllib: {e}")
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
        
        # Add more formats as needed
        return []
    
    except Exception as e:
        log.error(f"Failed to parse manifest {manifest_path}: {e}")
        return []
