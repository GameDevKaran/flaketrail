import json
import os
from pathlib import Path
from .engine import diagnose, list_scenarios

def main():
    directory=Path('artifacts');directory.mkdir(exist_ok=True)
    results=[diagnose(item['id']) for item in list_scenarios()]
    report={'application':'FlakeTrail','execution':'gitlab_ci_environment' if os.getenv('CI')=='true' and os.getenv('CI_PIPELINE_ID') else 'local','sourceCommit':os.getenv('CI_COMMIT_SHA'),'pipelineId':os.getenv('CI_PIPELINE_ID'),'pipelineUrl':os.getenv('CI_PIPELINE_URL'),'projectId':os.getenv('CI_PROJECT_ID'),'duoExecutionVerified':False,'results':results}
    (directory/'diagnosis-evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if any(item['status']!='minimized' or item['repair']['status']!='verified_finite' or item['repair']['negativeControl']['accepted'] for item in results):raise RuntimeError('A fixture repair gate failed; evidence preserved')
    print('Saved actual diagnosis evidence; CI metadata alone is not provider-verified Duo execution.')

if __name__=='__main__':main()
