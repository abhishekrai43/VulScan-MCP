#!/usr/bin/env python3
import requests
import json

packages = {
    '@angular/animations': '18.1.0',
    '@angular/common': '18.1.0',
    '@angular/compiler': '18.1.0',
    '@angular/core': '18.1.0',
    '@angular/forms': '18.1.0',
    '@angular/platform-browser': '18.1.0',
    '@angular/platform-browser-dynamic': '18.1.0',
    '@angular/router': '18.1.0',
    'angular-oauth2-oidc': '17.0.2',
    'primeicons': '7.0.0',
    'primeng': '17.18.8',
    'rxjs': '7.8.0',
    'tslib': '2.3.0',
    'zone.js': '0.14.3'
}

print('Checking npm packages against OSV database...\n')
print('='*60)

vulnerable_count = 0
for pkg, version in packages.items():
    try:
        response = requests.post(
            'https://api.osv.dev/v1/query',
            json={
                'package': {'name': pkg, 'ecosystem': 'npm'},
                'version': version
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            vulns = data.get('vulns', [])
            
            if vulns:
                vulnerable_count += 1
                print(f'\n❌ {pkg}@{version}')
                print(f'   Found {len(vulns)} vulnerability(ies):')
                for v in vulns[:5]:
                    vuln_id = v.get('id', 'Unknown')
                    summary = v.get('summary', 'No summary available')
                    severity = v.get('database_specific', {}).get('severity', 'UNKNOWN')
                    print(f'   - {vuln_id} [{severity}]')
                    print(f'     {summary[:80]}')
            else:
                print(f' {pkg}@{version}')
        else:
            print(f'⚠️  {pkg}@{version} - HTTP {response.status_code}')
            
    except Exception as e:
        print(f'⚠️  {pkg}@{version} - Error: {str(e)}')

print('\n' + '='*60)
print(f'Total packages checked: {len(packages)}')
print(f'Packages with vulnerabilities: {vulnerable_count}')
print(f'Clean packages: {len(packages) - vulnerable_count}')
