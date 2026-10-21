import {execFileSync} from 'node:child_process';
import fs from 'node:fs/promises';
await fs.mkdir('.local/container',{recursive:true});let id;const proof={application:'FlakeTrail',location:'local_linux_container',startedAt:new Date().toISOString(),passed:false,checks:[]};
try{
 id=execFileSync('docker',['run','--detach','--rm','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--memory','512m','--cpus','1','--pids-limit','64','-p','127.0.0.1::8786','flaketrail:local-check'],{encoding:'utf8'}).trim();if(!/^[a-f0-9]{64}$/.test(id))throw Error('Unexpected owned container ID');
 const config=JSON.parse(execFileSync('docker',['inspect',id],{encoding:'utf8'}))[0];const base='http://127.0.0.1:'+config.NetworkSettings.Ports['8786/tcp'][0].HostPort;
 let health;for(let i=0;i<30;i++){try{const response=await fetch(base+'/api/health');if(response.ok){health=await response.json();break;}}catch{}await new Promise(resolve=>setTimeout(resolve,250));}
 if(!health||health.sponsorExecution!=='not_verified')throw Error('Health/provenance mismatch');proof.checks.push('actual Linux HTTP health');
 const result=await(await fetch(base+'/api/diagnose',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scenario:'derived-cache',budget:40})})).json();
 if(result.status!=='minimized'||result.minimalOrder.length!==3||result.repair.status!=='verified_finite'||result.repair.negativeControl.accepted)throw Error('Linux diagnosis/repair failed');proof.checks.push('actual Linux subprocess minimization and assertion-preserving repair');proof.observed={runs:result.runs,elapsedMs:result.elapsedMs,minimalOrder:result.minimalOrder};
 const response=await fetch(base+'/api/diagnose',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://foreign.example'},body:'{}'});if(response.status!==403)throw Error('Origin check failed');proof.checks.push('cross-origin rejection');
 if(config.Config.User!=='10001:10001'||!config.HostConfig.ReadonlyRootfs)throw Error('Isolation mismatch');proof.checks.push('non-root read-only runtime');proof.image=config.Image;proof.passed=true;
}catch(error){proof.error=String(error);process.exitCode=1;}
finally{if(id&&/^[a-f0-9]{64}$/.test(id))execFileSync('docker',['stop',id],{stdio:'ignore'});proof.finishedAt=new Date().toISOString();await fs.writeFile('.local/container/verification.json',JSON.stringify(proof,null,2));console.log(JSON.stringify(proof,null,2));}
