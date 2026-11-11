import * as THREE from 'three';
import { entranceTiming, entranceVariables, sceneSessionKey } from './entrance-config.js';
import { OrbitControls } from './vendor/OrbitControls.js';

const $=id=>document.getElementById(id);
const motionPreference=matchMedia('(prefers-reduced-motion: reduce)');
let reduced=motionPreference.matches;
let restoredView=false;
const days=['10/23','10/24','10/25','10/26','10/27','10/28','10/29'];
const counts=[1,0,2,1,0,3,3];
const types=[{title:'人员目标检出',icon:'person',zone:'站台区域',key:'platform'},{title:'汽车目标检出',icon:'car',zone:'站前道路',key:'road'},{title:'区域停留提示',icon:'zone',zone:'站台区域',key:'platform'}];
const events=[];
days.forEach((day,d)=>{for(let n=0;n<counts[d];n++){let type=types[(d+n)%3];events.push({id:`DEMO-${d}-${n}`,day,...type,time:`${day.replace('/','-')} ${['14:23:10','13:56:22','11:48:37'][n]}`,pending:d===6&&n<2});}});
events.reverse();events.sort((a,b)=>b.time.localeCompare(a.time));
const pendingCounts=days.map(day=>events.filter(e=>e.day===day&&e.pending).length);
let selected=events[0], dayFilter=null, sceneApi=null, autoTimer, toastTimer;
function icon(name){return `<svg><use href="#${name}"/></svg>`;}
function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),3500);}
function modal(title,html){$('modalTitle').textContent=title;$('modalBody').innerHTML=html;$('modal').showModal();}
$('closeModal').onclick=()=>$('modal').close();
$('modal').addEventListener('click',e=>{if(e.target===$('modal')){const b=$('modal').getBoundingClientRect();if(e.clientX<b.left||e.clientX>b.right||e.clientY<b.top||e.clientY>b.bottom)$('modal').close();}});
function renderEvents(){
 const rows=events.filter(e=>!dayFilter||e.day===dayFilter);
 $('eventList').innerHTML=rows.length?rows.map(e=>`<button class="event-row ${e.id===selected.id?'active':''}" data-id="${e.id}" aria-pressed="${e.id===selected.id}"><span class="event-icon">${icon(e.icon)}</span><span class="event-content"><time>${e.time}</time><b>${e.title}</b><small>演示摄像头 · ${e.zone}</small></span><span class="status ${e.pending?'':'done'}">${e.pending?'待核查':'已处理'}</span></button>`).join(''):'<div class="empty">该日期没有示例告警<br>选择其他日期或清除筛选</div>';
 $('eventCount').textContent=`${rows.length} 条示例`;$('filterLabel').textContent=dayFilter?`${dayFilter} 的告警`:'全部日期';
 $('eventList').querySelectorAll('button').forEach(b=>b.onclick=()=>selectEvent(events.find(e=>e.id===b.dataset.id),true));
}
function updateEvidence(){
 $('evidenceTitle').textContent=selected.title;$('evidenceTime').textContent=selected.time;$('evidenceZone').textContent=`${selected.zone}（示意）`;
 $('evidenceStatus').textContent=selected.pending?'待核查':'已处理';$('evidenceStatus').className=`tag ${selected.pending?'amber':'green'}`;
}
function selectEvent(e,focus){selected=e;renderEvents();updateEvidence();if(focus){setView('evidence');sceneApi?.focus(e.key,e.title);}}
function setView(view){document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));}
function selection(title,text){$('selectionTitle').textContent=title;$('selectionText').textContent=text;}
const pendingPoints=pendingCounts.map((n,i)=>[50+i*100,92-n/3*70]);
const pendingPath=pendingPoints.map(([x,y],i)=>`${i?'L':'M'}${x} ${y}`).join(' ');
$('barChart').insertAdjacentHTML('afterbegin',`<svg class="pending-trend" viewBox="0 0 700 100" preserveAspectRatio="none" aria-hidden="true"><path d="${pendingPath}"/>${pendingPoints.map(([x,y],i)=>`<circle cx="${x}" cy="${y}" r="${pendingCounts[i]?3.6:2.1}"/>`).join('')}</svg>`);
days.forEach((d,i)=>{const b=document.createElement('button');b.dataset.day=d;b.setAttribute('aria-label',`${d}，${counts[i]}条告警，其中${pendingCounts[i]}条待核查，点击筛选`);b.innerHTML=`<span class="bar" data-value="${counts[i]}" style="height:${counts[i]/3*74}%"></span><span class="day">${d}</span>`;b.onclick=()=>{dayFilter=dayFilter===d?null:d;applyFilter();};$('barChart').append(b);});
function applyFilter(){renderEvents();$('clearFilter').hidden=!dayFilter;document.querySelectorAll('[data-day]').forEach(b=>b.classList.toggle('active',b.dataset.day===dayFilter));$('eventList').scrollTop=0;}
$('clearFilter').onclick=()=>{dayFilter=null;applyFilter();};
function autoScroll(){clearInterval(autoTimer);if(!$('autoScroll').checked||reduced)return;autoTimer=setInterval(()=>{const el=$('eventList');if(document.hidden||$('modal').open||el.matches(':hover')||el.contains(document.activeElement))return;const atEnd=el.scrollTop+el.clientHeight>=el.scrollHeight-4;el.scrollTo({top:atEnd?0:el.scrollTop+88,behavior:'smooth'});},4500);}
$('autoScroll').onchange=autoScroll;
$('previewImage').onclick=()=>modal('铁路现场参考素材','<img src="reference-scene.png" alt="用户提供的铁路现场原图"><p>这张图片来自你提供的现场素材，仅用于验证图片查看交互。示例事件未绑定真实告警截图，未在素材上伪造识别框。</p>');
$('recordingBtn').onclick=()=>modal('录像关联 · 交互说明',`<p><strong>${selected.title} · ${selected.time}</strong></p><p>正式接入时，根据同一摄像头、录像开始时间与结束时间，查找覆盖事件时刻的录像，并定位播放进度。</p><p>当前样板没有接入业务录像，因此不提供虚构的播放结果。原系统手动录像与回放方式保持不变。</p>`);
const helpContent='<p><strong>可以实际操作的内容</strong></p><ul><li>拖动模型旋转、滚轮缩放、右键平移；“总览”恢复初始视角，“俯视”检查轨道布局。</li><li>点击摄像头标记或左侧设备卡：聚焦设备，显示覆盖示意。</li><li>点击右侧告警：聚焦关联的站台或道路区域，并同步右下角事件信息。</li><li>“隐藏雨棚”移开遮挡；“覆盖示意”开关控制覆盖图层。</li><li>点击趋势图日期筛选事件；滚动列表，或开启自动轮播，鼠标悬停/键盘焦点进入时暂停。</li><li>点击证据图片可以放大。录像按钮说明真实接入方式。</li></ul><p>场景为自建简化三维模型；位置、区域、设备状态、告警为示例。交互只影响此样板，不写入正式系统。</p>';
$('helpBtn').onclick=()=>modal('样板操作说明',helpContent);
$('designInfo').onclick=()=>modal('设计与交互依据',`<p>结合<a href="https://www.zcool.com.cn/work/ZNjM1ODIzODg=.html" target="_blank" rel="noopener">《智慧车站管控平台》</a>的三列布局、文字层级、语义颜色与轻边框组件，参考<a href="https://www.zcool.com.cn/work/ZNTU0NTgxMDQ=.html" target="_blank" rel="noopener">《天脉｜智慧车站可视化系统》</a>展示的场景选中、区域突出与信息联动。</p><p>字号采用桌面阅读尺度：主标题28–30px、模块16–17px、正文12–14px；颜色为深蓝背景、蓝色操作、青色在线、橙色待核查。柱形图表达次数，圆环表达处理状态。使用可读取文字和符号配合颜色。</p>${helpContent}`);
renderEvents();updateEvidence();

async function initScene(){
 const host=$('sceneCanvas'), stage=$('stage');
 const renderer=new THREE.WebGLRenderer({antialias:true,alpha:true,powerPreference:'high-performance'});
 renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.setClearColor(0x000000,0);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.13;host.append(renderer.domElement);
 // Fixed lighting and geometry let the shadow map persist between layer changes.
 renderer.shadowMap.autoUpdate = false;
 renderer.shadowMap.needsUpdate = true;
 const scene=new THREE.Scene(), camera=new THREE.OrthographicCamera(-30,30,18,-18,.1,250);camera.position.set(38,32,42);
 const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(0,1,0);controls.enableDamping=true;controls.dampingFactor=.09;controls.minPolarAngle=.1;controls.maxPolarAngle=Math.PI*.46;controls.minZoom=.6;controls.maxZoom=3;controls.enablePan=true;controls.update();
 scene.add(new THREE.HemisphereLight(0xe2e9eb,0x655d53,1.75));
 const sun=new THREE.DirectionalLight(0xffedd5,2.65);sun.position.set(-22,30,17);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-40,right:40,top:40,bottom:-40,near:1,far:100});sun.shadow.bias=-.001;sun.shadow.normalBias=.04;scene.add(sun);
 const fill=new THREE.DirectionalLight(0xaabfc7,.68);fill.position.set(25,12,-20);scene.add(fill);
 const root=new THREE.Group();scene.add(root);const canopy=new THREE.Group();root.add(canopy);
 function material(color, metalness = .08, roughness = .76) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
 }
 function surfaceTexture(kind, repeatX, repeatY) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 256;
  const ctx = canvas.getContext('2d');
  let seed = 23;
  const random = () => {
   seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
   return seed / 4294967296;
  };
  const gravel = kind === 'ballast';
  ctx.fillStyle = gravel ? '#969087' : '#d1cfc8';
  ctx.fillRect(0, 0, 256, 256);
  for (let i = 0; i < (gravel ? 2900 : 1600); i++) {
   const shade = Math.floor(90 + random() * 155);
   ctx.fillStyle = `rgba(${shade},${shade},${shade},${gravel ? .8 : .22})`;
   ctx.fillRect(random() * 256, random() * 256, 1 + random() * (gravel ? 4 : 2), 1 + random() * 2);
  }
  if (kind === 'roof' || kind === 'wall' || kind === 'paving') {
   ctx.strokeStyle = 'rgba(55,53,49,.23)';
   ctx.lineWidth = 1;
   for (let i = 0; i < 256; i += kind === 'roof' ? 32 : 64) {
    ctx.beginPath();
    ctx.moveTo(i + .5, 0);
    ctx.lineTo(i + .5, 256);
    if (kind !== 'roof') {
     ctx.moveTo(0, i + .5);
     ctx.lineTo(256, i + .5);
    }
    ctx.stroke();
   }
  }
  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(repeatX, repeatY);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
  return texture;
 }
 function textured(color, kind, repeatX, repeatY, metalness = 0, roughness = .9) {
  const result = material(color, metalness, roughness);
  result.map = surfaceTexture(kind, repeatX, repeatY);
  return result;
 }
 const mat = {
  base: material(0x424d53), ground: textured(0x787d72, 'ground', 5, 4),
  platform: material(0x877f6d), roof: textured(0x74868a, 'roof', 4, 2, .28, .7),
  canopyRoof: textured(0xabb8b7, 'roof', 6, 1, .24, .72),
  wall: textured(0xc1a17d, 'wall', 3, 1),
  wing: textured(0xad957e, 'wall', 2, 1),
  edge: material(0x657e81, .24), steel: material(0x747e7e, .45),
  rail: material(0xb9c2be, .55, .46), tie: material(0x847465),
  white: material(0xe0e2d8, .19), glass: material(0x315966, .28, .36),
  darkglass: material(0x24383e, .25, .46), yellow: material(0xd2a34d),
  green: material(0x526d49), trunk: material(0x665746),
  road: textured(0x4f5759, 'ground', 7, 1),
  ballast: textured(0x77726a, 'ballast', 9, 1),
  paving: textured(0xb4ad9e, 'paving', 9, 1)
 };
 const unitBox=new THREE.BoxGeometry(1,1,1), unitCylinder=new THREE.CylinderGeometry(1,1,1,10);
 function box(w,h,d,x,y,z,m,parent=root){const mesh=new THREE.Mesh(unitBox,m);mesh.scale.set(w,h,d);mesh.position.set(x,y,z);mesh.castShadow=true;mesh.receiveShadow=true;parent.add(mesh);return mesh;}
 function beam(a,b,r,m,parent=root){const av=new THREE.Vector3(...a),bv=new THREE.Vector3(...b),len=av.distanceTo(bv);const mesh=new THREE.Mesh(unitCylinder,m);mesh.scale.set(r,len,r);mesh.position.copy(av).add(bv).multiplyScalar(.5);mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),bv.sub(av).normalize());mesh.castShadow=true;parent.add(mesh);return mesh;}
 function instances(positions,geometry,m){const inst=new THREE.InstancedMesh(geometry,m,positions.length),dummy=new THREE.Object3D();positions.forEach((p,i)=>{dummy.position.set(...p.p);dummy.scale.set(...p.s);dummy.updateMatrix();inst.setMatrixAt(i,dummy.matrix);});inst.castShadow=true;inst.receiveShadow=true;root.add(inst);return inst;}
 function lines(points,color,parent=root,opacity=1){const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints(points.map(p=>new THREE.Vector3(...p))),new THREE.LineBasicMaterial({color,transparent:opacity<1,opacity}));parent.add(line);return line;}
 box(47,.75,30,0,-.48,0,mat.base);box(46.6,.12,29.6,0,-.045,0,mat.ground);
 // Architectural base, landscaped rear edge and a station-side access road.
 box(45,.03,3.6,0,.04,-12.3,mat.road);
 const roadLines=[];for(let x=-21;x<22;x+=2.6)roadLines.push({p:[x,.065,-12.3],s:[1.3,.02,.06]});instances(roadLines,unitBox,mat.white);
 box(31,.23,6,0,.14,-7.4,mat.paving);
 const station=new THREE.Group();root.add(station);
 box(20,4.4,4.6,0,2.5,-7.5,mat.wall,station);box(20.25,.3,4.9,0,4.85,-7.5,mat.roof,station);
 box(20.1,2.65,.07,0,2.8,-5.16,mat.glass,station);box(20.1,2.65,.07,0,2.8,-9.84,mat.glass,station);
 for(let side of [-1,1]){for(let x of [-8,-4,0,4,8])box(.07,2.4,.08,x,2.8,side<0?-9.8:-5.12,mat.white,station);}
 for(let x of [-8.5,-4.5,0,4.5,8.5]){box(1.25,.14,.09,x,1.2,-5.01,mat.steel,station);box(1.25,.14,.09,x,3.2,-5.01,mat.steel,station);}
 box(9,2.5,4.3,-14,1.5,-7.5,mat.wing,station);box(9.3,.22,4.6,-14,2.9,-7.5,mat.roof,station);
 box(7,2.5,4.3,13,1.5,-7.5,mat.wing,station);box(7.3,.22,4.6,13,2.9,-7.5,mat.roof,station);
 const mullions=[];for(let x=-9.7;x<10;x+=.85){mullions.push({p:[x,2.85,-5.08],s:[.055,2.7,.13]});mullions.push({p:[x,2.85,-9.92],s:[.055,2.7,.13]});}instances(mullions,unitBox,mat.white);
 for(let y of [1.5,2.8,4.1])box(20,.06,.13,0,y,-5.06,mat.white,station);
 box(7,.2,1.8,0,1.7,-4.5,mat.roof,station);for(let x of [-3.1,3.1])beam([x,.3,-3.8],[x,1.6,-3.8],.07,mat.steel,station);
 // Repeated roof ribs and rooftop plant give the building scale.
 for(let x=-9;x<10;x+=1.2)box(.04,.07,4.8,x,5.04,-7.5,mat.edge,station);
 for(let x=-8;x<9;x+=3.2){box(2.25,.025,1.1,x,5.06,-7.7,mat.darkglass,station);for(let xx of [-1.1,0,1.1])box(.04,.035,1.1,x+xx,5.085,-7.7,mat.edge,station);}
 for(let x of [-5,2,6]){box(1.8,.55,1,x,5.2,-7.5,mat.steel,station);for(let z=-7.9;z<-7;z+=.15)box(1.6,.02,.035,x,5.49,z,mat.darkglass,station);}
 function textPlane(text,x,y,z,width,parent=root){const c=document.createElement('canvas');c.width=1024;c.height=160;const ctx=c.getContext('2d');ctx.fillStyle='#edf8ff';ctx.font='bold 78px Microsoft YaHei';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(text,512,80);const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;const p=new THREE.Mesh(new THREE.PlaneGeometry(width,width*.156),new THREE.MeshBasicMaterial({map:t,transparent:true,depthWrite:false}));p.position.set(x,y,z);parent.add(p);return p;}
 textPlane('视 界 巡 警 · 示 意 站 场',0,4.58,-5.12,10,station);
 const trackZ=[-2.6,.0,6.3,8.9];const ties=[];
 for(const z of trackZ){box(45,.12,1.9,0,.06,z,mat.ballast);for(let x=-22;x<=22;x+=.55)ties.push({p:[x,.15,z],s:[.15,.08,1.75]});for(let side of [-.62,.62])box(45,.095,.065,0,.24,z+side,mat.rail);}
 instances(ties,unitBox,mat.tie);
 for(const z of [3.15,11.65]){
  box(38,.56,3,0,.34,z,mat.platform);
  box(38,.02,3,0,.63,z,mat.paving);
  for(const side of [-1.28,1.28])box(37,.025,.08,0,.66,z+side,mat.yellow);
  box(36,.15,3.35,0,3.45,z,mat.canopyRoof,canopy);box(36,.14,.18,0,3.62,z,mat.edge,canopy);
  for(let x=-15;x<16;x+=5.5){box(2.7,.03,.72,x,3.55,z,mat.glass,canopy);box(.04,.04,.74,x,3.575,z,mat.white,canopy);}
  for(let x=-16;x<=16;x+=4){beam([x,.64,z],[x,3.35,z],.08,mat.steel);beam([x,2.5,z],[x,3.3,z-1.3],.05,mat.steel,canopy);beam([x,2.5,z],[x,3.3,z+1.3],.05,mat.steel,canopy);box(.06,.06,3.3,x,3.59,z,mat.edge,canopy);}
  const ribs=[];for(let x=-17.6;x<18;x+=.5)ribs.push({p:[x,3.58,z],s:[.025,.03,3.3]});const roofRibs=new THREE.InstancedMesh(unitBox,mat.white,ribs.length),dummy=new THREE.Object3D();ribs.forEach((p,i)=>{dummy.position.set(...p.p);dummy.scale.set(...p.s);dummy.updateMatrix();roofRibs.setMatrixAt(i,dummy.matrix);});canopy.add(roofRibs);
  for(let x of [-11,1,10]){box(1.4,.1,.45,x,1.02,z,mat.steel);for(let xx of [-.5,.5])box(.07,.4,.35,x+xx,.82,z,mat.darkglass);}
  for(let x of [-13,4,14]){beam([x,.7,z],[x,2.5,z],.035,mat.steel);box(.9,.48,.08,x,2.65,z,mat.glass,canopy);box(.7,.03,.1,x,2.65,z+.06,mat.white,canopy);}
  for(let x of [-8,8]){box(1.5,.05,.52,x,.68,z,mat.steel);beam([x-.65,.68,z],[x-.65,1.2,z],.03,mat.steel);beam([x+.65,.68,z],[x+.65,1.2,z],.03,mat.steel);}
 }
 // Static reference train: no simulated detection, no fictitious train telemetry.
 const train=new THREE.Group();root.add(train);const trainZ=6.3;
 for(let n=0;n<4;n++){let x=-12+n*7;box(6.6,1.35,1.45,x,1.2,trainZ,mat.white,train);box(6.7,.08,1.5,x,1.25,trainZ,mat.edge,train);box(6.4,.18,1.3,x,1.94,trainZ,mat.roof,train);box(6.4,.15,1.2,x,.48,trainZ,mat.darkglass,train);for(let t=-2.7;t<=2.8;t+=.85)for(let side of [-.731,.731])box(.54,.47,.018,x+t,1.51,trainZ+side,mat.darkglass,train);for(let axle of [-2.35,2.35])for(let side of [-.6,.6]){const wheel=new THREE.Mesh(new THREE.CylinderGeometry(.19,.19,.12,14),mat.steel);wheel.rotation.x=Math.PI/2;wheel.position.set(x+axle,.43,trainZ+side);train.add(wheel);}if(n<3)box(.13,.7,1.1,x+3.43,1.27,trainZ,mat.steel,train);}
 const nose=new THREE.Mesh(new THREE.SphereGeometry(1,24,12),mat.white);nose.scale.set(2.2,.75,.77);nose.position.set(13.15,1.21,trainZ);train.add(nose);box(.95,.12,1.25,14,1.02,trainZ,mat.edge,train);box(.68,.26,1.1,13.9,1.53,trainZ,mat.darkglass,train);
 for(let x of [-17,-3,11]){box(.24,.05,.7,x,2.08,trainZ,mat.steel,train);beam([x,2.1,trainZ],[x+.5,2.6,trainZ],.018,mat.steel,train);beam([x+.5,2.6,trainZ],[x+1,2.1,trainZ],.018,mat.steel,train);}
 // Overhead gantries and wires, intentionally restrained to preserve readability.
 for(let x=-20;x<=20;x+=10){for(let z of [-4.1,10.3])beam([x,.1,z],[x,5.6,z],.075,mat.steel);beam([x,5.6,-4.1],[x,5.6,10.3],.06,mat.steel);for(let z of trackZ)beam([x,5.6,z],[x,4.6,z],.02,mat.steel);}
 for(let z of trackZ)lines([[-22,4.6,z],[22,4.6,z]],0x86a9b8,root,.45);
 // Trees and verge strips supply scale while leaving the station silhouette clear.
 const treeGeo=new THREE.IcosahedronGeometry(.6,1);
 for(let i=0;i<19;i++){let x=-21+i*2.4,z=-10.6;box(.07,.85,.07,x,.45,z,mat.trunk);let tree=new THREE.Mesh(treeGeo,mat.green);tree.scale.set(.7,1.5,.7);tree.position.set(x,1.35,z);tree.castShadow=true;root.add(tree);}
 for(let x=-20;x<22;x+=4){box(2.2,.12,.7,x,.11,14,mat.green);}
 // Interactive camera and a schematic footprint, not a calibrated frustum.
 const cameraPos=new THREE.Vector3(-10,4.3,3.15);const device=new THREE.Group();device.position.copy(cameraPos);root.add(device);
 beam([-10,.6,3.15],[-10,4.1,3.15],.07,mat.steel);box(.45,.15,.3,0,0,0,mat.steel,device);box(.85,.35,.36,.25,.25,0,mat.white,device);const lens=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,.07,16),mat.darkglass);lens.rotation.z=Math.PI/2;lens.position.set(.71,.25,0);device.add(lens);
 const cameraRing=new THREE.Mesh(new THREE.RingGeometry(.35,.43,40),new THREE.MeshBasicMaterial({color:0x55aebb,side:THREE.DoubleSide,transparent:true,opacity:.8,depthTest:false}));cameraRing.position.copy(cameraPos).add(new THREE.Vector3(0,.85,0));root.add(cameraRing);
 const hit=new THREE.Mesh(new THREE.SphereGeometry(.9,12,8),new THREE.MeshBasicMaterial({transparent:true,opacity:0,depthWrite:false}));hit.position.copy(cameraPos);root.add(hit);
 const footprint=[[-8,.72,1.9],[6,.72,1.9],[6,.72,4.4],[-8,.72,4.4]];
 const coverage=new THREE.Group();root.add(coverage);
 const coverageGeo=new THREE.BufferGeometry().setFromPoints(footprint.map(v=>new THREE.Vector3(...v)));coverageGeo.setIndex([0,1,2,0,2,3]);coverageGeo.computeVertexNormals();coverage.add(new THREE.Mesh(coverageGeo,new THREE.MeshBasicMaterial({color:0x648f93,transparent:true,opacity:.10,side:THREE.DoubleSide,depthWrite:false})));
 lines([...footprint,footprint[0]],0x80a8a7,coverage,.52);
 for(let n=0;n<4;n++){const vs=[cameraPos.toArray(),footprint[n],footprint[(n+1)%4]];const geo=new THREE.BufferGeometry().setFromPoints(vs.map(v=>new THREE.Vector3(...v)));geo.computeVertexNormals();coverage.add(new THREE.Mesh(geo,new THREE.MeshBasicMaterial({color:0x71969b,transparent:true,opacity:.065,side:THREE.DoubleSide,depthWrite:false})));lines([cameraPos.toArray(),footprint[n]],0x729497,coverage,.26);}
 const zoneMat=new THREE.MeshBasicMaterial({color:0xffb641,transparent:true,opacity:.22,side:THREE.DoubleSide,depthWrite:false});
 const zoneMesh=new THREE.Mesh(new THREE.PlaneGeometry(14,2.45),zoneMat);zoneMesh.rotation.x=-Math.PI/2;zoneMesh.position.set(-1,.75,3.15);zoneMesh.visible=false;root.add(zoneMesh);
 const roadMesh=new THREE.Mesh(new THREE.PlaneGeometry(13,3.5),zoneMat.clone());roadMesh.rotation.x=-Math.PI/2;roadMesh.position.set(-1,.10,-12.3);roadMesh.visible=false;root.add(roadMesh);
 const shadowGround=new THREE.Mesh(new THREE.PlaneGeometry(110,110),new THREE.ShadowMaterial({opacity:.30}));shadowGround.rotation.x=-Math.PI/2;shadowGround.position.y=-.91;shadowGround.receiveShadow=true;scene.add(shadowGround);
 const displayGroundMaterial = new THREE.ShaderMaterial({
  transparent: true,
  depthWrite: false,
  vertexShader: `
   varying vec2 groundPosition;
   void main() {
    groundPosition = position.xy;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
   }
  `,
  fragmentShader: `
   varying vec2 groundPosition;

   float gridLine(vec2 point, float spacing) {
    vec2 cell = point / spacing;
    vec2 width = max(fwidth(cell), vec2(.0001));
    vec2 distanceToLine = abs(fract(cell - .5) - .5);
    vec2 coverage = 1.0 - smoothstep(width * .4, width * 1.3, distanceToLine);
    return max(coverage.x, coverage.y);
   }

   void main() {
    vec2 p = groundPosition;
    float falloff = 1.0 - smoothstep(.4, 1.0, length(p / vec2(46.0, 34.0)));
    vec2 edge = abs(p) - vec2(26.0, 17.5);
    float borderDistance = abs(max(edge.x, edge.y));
    float border = 1.0 - smoothstep(.04, .20 + fwidth(borderDistance), borderDistance);
    float fine = gridLine(p, 3.0);
    float coarse = gridLine(p, 12.0);
    // Engraved reference ticks follow the model base, independent of the camera view.
    float graduation = abs(fract(p.x * .5 + .5) - .5);
    float tickWidth = max(fwidth(graduation), .01);
    float tick = 1.0 - smoothstep(tickWidth * .35, tickWidth * 1.1, graduation);
    float major = 1.0 - step(.10, abs(fract(p.x / 8.0 + .5) - .5));
    float edgeOffset = abs(p.y) - 17.5;
    float ticks = tick * step(abs(p.x), 26.0) * smoothstep(.12, .28, edgeOffset)
      * (1.0 - smoothstep(.48 + .35 * major, .62 + .35 * major, edgeOffset));
    float keyLight = 1.0 - smoothstep(-.72, .80, dot(p / vec2(38.0, 28.0), vec2(.72, -.69)));
    float grainVisibility = 1.0 - smoothstep(.08, .22, length(fwidth(p)));
    float grain = fract(sin(dot(floor(p * vec2(18.0, 70.0)), vec2(27.13, 71.27))) * 43758.5453);
    vec3 slate = mix(vec3(.034, .071, .12), vec3(.075, .147, .224), falloff * mix(.56, 1.0, keyLight));
    slate += vec3(.052, .067, .072) * (fine * .24 + coarse * .48);
    slate = mix(slate, vec3(.23, .39, .53), (border * .42 + ticks * .60) * mix(.65, 1.0, keyLight));
    slate += (grain - .5) * .022 * grainVisibility;
    gl_FragColor = vec4(slate, falloff * .92);
   }
  `
 });
 const displayGround = new THREE.Mesh(new THREE.PlaneGeometry(100, 80), displayGroundMaterial);
 displayGround.rotation.x = -Math.PI / 2;
 displayGround.position.y = -.96;
 // Composite the presentation surface before the existing contact shadow.
 displayGround.renderOrder = -2;
 shadowGround.renderOrder = -1;
 scene.add(displayGround);
 let tween=null,roofHidden=false,raf=0,frame=0,lastRender=0;
 function resize(){const {width,height}=host.getBoundingClientRect();if(!width||!height)return;const aspect=width/height,half=Math.max(17.5,29/aspect);camera.left=-half*aspect;camera.right=half*aspect;camera.top=half;camera.bottom=-half;camera.updateProjectionMatrix();renderer.setSize(width,height,false);}
 const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(host);resize();
 function transition(pos,target,zoom=1){const duration=reduced?0:400;tween={from:camera.position.clone(),to:new THREE.Vector3(...pos),fromTarget:controls.target.clone(),toTarget:new THREE.Vector3(...target),fromZoom:camera.zoom,toZoom:zoom,start:performance.now(),duration};}
 function setActiveView(view) {
  $('resetView').setAttribute('aria-pressed', String(view === 'overview'));
  $('topView').setAttribute('aria-pressed', String(view === 'top'));
 }
 controls.addEventListener('start', () => {
  finishEntrance(true);
  tween = null;
  setActiveView(null);
  $('viewStatus').textContent = '视角：自由观察';
 });
 let activeMarker = null;
 function highlight(key) {
  activeMarker = key;
  zoneMesh.visible = key === 'platform';
  roadMesh.visible = key === 'road';
  $('cameraPin').classList.toggle('active', key === 'device');
  $('zonePin').classList.toggle('active', key === 'platform');
  $('cameraPin').setAttribute('aria-pressed', String(key === 'device'));
  $('zonePin').setAttribute('aria-pressed', String(key === 'platform'));
  stage.classList.toggle('has-marker-selection', Boolean(key));
 }
 let deviceName = '';
 const pin = $('cameraPin');
 const pinName = $('cameraPinName');
 const pinStatus = $('cameraPinStatus');
 const pinId = $('cameraPinId');
 const pinDetail = $('cameraPinDetail');
 const deviceColors = { online: 0x54a68a, offline: 0x91a0aa, unknown: 0x657680 };
 function focus(key,title){
  finishEntrance(true);
  setActiveView(null);
  if(key==='device'){transition([16,15,24],[-8,2,3],1.85);coverage.visible=true;$('toggleCoverage').classList.add('selected');$('toggleCoverage').setAttribute('aria-pressed','true');highlight('device');selection(deviceName || '演示摄像头','模型位置与覆盖范围为示意');$('viewStatus').textContent='视角：设备定位';}
  else if(key==='road'){transition([23,28,-35],[-1,1,-11],1.5);highlight('road');selection(title||'站前道路','仅展示设备与区域的示例关联，不表示目标世界坐标');$('viewStatus').textContent='视角：道路区域';}
  else {transition([23,23,32],[-1,1,3],1.5);highlight('platform');selection(title||'站台区域',document.documentElement.classList.contains('embedded') ? '站台范围为模型示意，可隐藏雨棚查看。' : '示例停留阈值 2 秒；可隐藏雨棚检查遮挡区域');$('viewStatus').textContent='视角：站台区域';}
 }
 function reset(){finishEntrance(true);setActiveView('overview');transition([38,32,42],[0,1,0],1);highlight(null);selection('场景总览','点击设备或告警，查看空间关联');$('viewStatus').textContent='视角：总览';setView('overview');}
 sceneApi={focus,reset};
 $('deviceCard').onclick=$('cameraPin').onclick=()=>{setView('device');focus('device');};$('zonePin').onclick=$('ruleZone').onclick=()=>{setView('zone');focus('platform');};$('locateEvent').onclick=()=>{setView('evidence');focus(selected.key,selected.title);};
 if (window.parent !== window) {
  const notifyParent = (action, marker) => window.parent.postMessage({ channel: 'rail-scene-v2', action, marker }, location.origin);
  window.addEventListener('message', event => {
   if (event.origin !== location.origin || event.source !== window.parent || event.data?.channel !== 'rail-home-v2') return;
   const { action, marker } = event.data;
   if (action === 'reset') reset();
   if (action === 'interrupt-entrance') finishEntrance(true);
   if (action === 'highlight-only' && marker === 'CAM-01') highlight('device');
   if (action === 'focus' && marker === 'CAM-01') focus('device');
   if (action === 'clear-highlight' && marker === 'CAM-01') {
    highlight(null);
    selection('场景总览', '点击设备或告警，查看空间关联');
   }
   if (action === 'device-state' && marker === 'CAM-01') {
    const { id, name, state, detail } = event.data;
    if (typeof id !== 'string' || typeof name !== 'string' || typeof detail !== 'string' ||
        !Object.hasOwn(deviceColors, state)) return;
    const mapped = /^\d+$/.test(id);
    deviceName = mapped ? name : '';
    pinName.textContent = deviceName || '演示摄像头';
    pinId.textContent = mapped ? '#' + id : '示意位置';
    pinStatus.hidden = !mapped;
    pinStatus.textContent = ({ online: '在线', offline: '离线', unknown: '未知' })[state];
    pinStatus.dataset.state = state;
    pinDetail.textContent = mapped ? detail + ' · 模型位置示意' : '尚未关联实际设备';
    cameraRing.material.color.setHex(deviceColors[state]);
    pin.dataset.state = state;
   }
  });
  $('cameraPin').addEventListener('click', () => notifyParent('device', 'CAM-01'));
  $('zonePin').addEventListener('click', () => notifyParent('region', 'platform'));
  $('resetView').addEventListener('click', () => notifyParent('reset'));
  $('clearSelection').addEventListener('click', () => notifyParent('reset'));
 }
 $('resetView').onclick=$('clearSelection').onclick=reset;
 $('topView').onclick=()=>{finishEntrance(true);setActiveView('top');transition([0,60,1],[0,0,0],1.08);$('viewStatus').textContent='视角：俯视';};
 $('toggleRoof').onclick=()=>{finishEntrance(true);roofHidden=!roofHidden;canopy.visible=!roofHidden;renderer.shadowMap.needsUpdate=true;$('toggleRoof').classList.toggle('selected',roofHidden);$('toggleRoof').setAttribute('aria-pressed',String(roofHidden));$('toggleRoof').innerHTML=icon('layers')+(roofHidden?'显示雨棚':'隐藏雨棚');toast(roofHidden?'已隐藏雨棚，便于查看站台区域':'已恢复雨棚');};
 $('toggleCoverage').onclick=()=>{finishEntrance(true);coverage.visible=!coverage.visible;$('toggleCoverage').classList.toggle('selected',coverage.visible);$('toggleCoverage').setAttribute('aria-pressed',String(coverage.visible));};
 document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{setView(b.dataset.view);if(b.dataset.view==='overview')reset();else if(b.dataset.view==='device')focus('device');else if(b.dataset.view==='zone')focus('platform');else focus(selected.key,selected.title);});
 const raycaster=new THREE.Raycaster(),mouse=new THREE.Vector2();let down=null;
 renderer.domElement.addEventListener('pointerdown',e=>{down=[e.clientX,e.clientY];});
 renderer.domElement.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>5)return;const rect=renderer.domElement.getBoundingClientRect();mouse.set((e.clientX-rect.left)/rect.width*2-1,-(e.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(mouse,camera);if(raycaster.intersectObject(hit).length){$('cameraPin').click();}});
 const projected = new THREE.Vector3();
 const labelObserver = new ResizeObserver(entries => {
  for (const entry of entries) {
   const marker = markers.find(item => item.element === entry.target);
   if (marker) {
    marker.width = entry.target.offsetWidth;
    marker.height = entry.target.offsetHeight;
   }
  }
 });
 const svgNS = 'http://www.w3.org/2000/svg';
 const guideLayer = document.createElementNS(svgNS, 'svg');
 guideLayer.classList.add('marker-guides');
 guideLayer.setAttribute('aria-hidden', 'true');
 stage.append(guideLayer);
 const markers = [
  { key: 'device', element: pin, anchor: device.localToWorld(new THREE.Vector3(.25, .25, 0)) },
  { key: 'platform', element: $('zonePin'), anchor: new THREE.Vector3(4.5, .75, 3.15) }
 ].map(marker => {
  const line = document.createElementNS(svgNS, 'line');
  const dot = document.createElementNS(svgNS, 'circle');
  dot.setAttribute('r', '2.5');
  guideLayer.append(line, dot);
  labelObserver.observe(marker.element);
  return { ...marker, line, dot, width: marker.element.offsetWidth, height: marker.element.offsetHeight };
 });
 function layoutMarkers() {
  const width = host.clientWidth;
  const height = host.clientHeight;
  const occupied = [];
  const ordered = activeMarker === 'platform' ? [markers[1], markers[0]] : markers;
  const tools = stage.querySelector('.scene-tools');
  const toolReserve = Math.max(64, height - tools.offsetTop + 8);
  for (const marker of ordered) {
   projected.copy(marker.anchor).project(camera);
   const x = (projected.x * .5 + .5) * width;
   const y = (-projected.y * .5 + .5) * height;
   const visible = projected.z >= -1 && projected.z <= 1 && x >= 0 && x <= width && y >= 0 && y <= height;
   const w = marker.width;
   const h = marker.height;
   const topLimit = 56;
   const bottomLimit = height - toolReserve - h;
   const clamp = THREE.MathUtils.clamp;
   const right = [x + 24, y - h / 2];
   const left = [x - w - 24, y - h / 2];
   const exterior = x < width / 2 ? left : right;
   const interior = x < width / 2 ? right : left;
   const options = [exterior, [x - w / 2, y - h - 24], interior, [x - w / 2, y + 24]];
   let rect = null;
   if (visible && bottomLimit >= topLimit) {
    for (const [left, top] of options) {
     const candidate = { left: clamp(left, 8, Math.max(8, width - w - 8)), top: clamp(top, topLimit, bottomLimit) };
     const collides = occupied.some(other => candidate.left < other.left + other.w + 8 &&
      candidate.left + w + 8 > other.left && candidate.top < other.top + other.h + 8 &&
      candidate.top + h + 8 > other.top);
     const coversAnchor = x >= candidate.left - 5 && x <= candidate.left + w + 5 &&
      y >= candidate.top - 5 && y <= candidate.top + h + 5;
     if (!collides && !coversAnchor) {
      rect = { ...candidate, w, h };
      break;
     }
    }
   }
   marker.element.style.visibility = rect ? 'visible' : 'hidden';
   marker.line.style.visibility = rect ? 'visible' : 'hidden';
   marker.dot.style.visibility = visible ? 'visible' : 'hidden';
   if (!visible) continue;
   marker.dot.setAttribute('cx', Math.round(x));
   marker.dot.setAttribute('cy', Math.round(y));
   const active = marker.key === activeMarker;
   marker.dot.classList.toggle('active', active);
   marker.line.classList.toggle('active', active);
   if (!rect) continue;
   occupied.push(rect);
   marker.element.style.left = `${Math.round(rect.left)}px`;
   marker.element.style.top = `${Math.round(rect.top)}px`;
   marker.line.setAttribute('x1', Math.round(x));
   marker.line.setAttribute('y1', Math.round(y));
   marker.line.setAttribute('x2', Math.round(clamp(x, rect.left, rect.left + w)));
   marker.line.setAttribute('y2', Math.round(clamp(y, rect.top, rect.top + h)));
  }
 }
 $('loading').hidden=true;
 for (const [name,value] of Object.entries(entranceVariables)) stage.style.setProperty(name,value);
 const fullEntrance = new URLSearchParams(location.search).get('entrance') === 'full' && !reduced;
 let entranceStart = null, outline = null, materialStates = [], lastSave = 0, lastSaved = '';
 const solidProgress={value:0};
 function saveView() {
  if (entranceStart !== null) return;
  const data = {position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom,
   roofHidden,coverage:coverage.visible,marker:activeMarker,view:$('topView').getAttribute('aria-pressed') === 'true' ? 'top' : $('resetView').getAttribute('aria-pressed') === 'true' ? 'overview' : null};
  const value=JSON.stringify(data);
  if (value===lastSaved) return;
  try { sessionStorage.setItem(sceneSessionKey,value); lastSaved=value; } catch {}
 }
 function restoreView() {
  try {
   const saved=JSON.parse(sessionStorage.getItem(sceneSessionKey));
   const vector=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&Math.abs(n)<250);
   if(!saved||!vector(saved.position)||!vector(saved.target)||!Number.isFinite(saved.zoom)) return;
   camera.position.fromArray(saved.position);controls.target.fromArray(saved.target);
   camera.zoom=THREE.MathUtils.clamp(saved.zoom,.6,3);camera.updateProjectionMatrix();
   roofHidden=saved.roofHidden===true;canopy.visible=!roofHidden;
   coverage.visible=saved.coverage===true;
   $('toggleRoof').classList.toggle('selected',roofHidden);
   $('toggleRoof').setAttribute('aria-pressed',String(roofHidden));
   $('toggleRoof').innerHTML=icon('layers')+(roofHidden?'显示雨棚':'隐藏雨棚');
   $('toggleCoverage').classList.toggle('selected',coverage.visible);
   $('toggleCoverage').setAttribute('aria-pressed',String(coverage.visible));
   highlight(['device','platform','road'].includes(saved.marker)?saved.marker:null);
   setActiveView(saved.view);$('viewStatus').textContent='视角：'+(saved.view==='top'?'俯视':saved.view==='overview'?'总览':'自由观察');
   renderer.shadowMap.needsUpdate=true;controls.update();restoredView=true;
  } catch {}
 }
 function finishEntrance(takeover=false) {
  if (entranceStart===null) return;
  entranceStart=null;
  root.visible=true;
  for(const [material,compile,cacheKey] of materialStates) {
   material.onBeforeCompile=compile;material.customProgramCacheKey=cacheKey;material.needsUpdate=true;
  }
  guideLayer.style.removeProperty('opacity');
  for(const marker of markers){marker.element.style.removeProperty('opacity');marker.element.style.removeProperty('clip-path');}
  materialStates=[];
  shadowGround.material.opacity=.30;
  renderer.shadowMap.needsUpdate=true;
  if(outline){scene.remove(outline);outline.geometry.dispose();outline.material.dispose();outline=null;}
  stage.dataset.entrance='complete';
  if(takeover) {
   tween=null;
   if(window.parent!==window) window.parent.postMessage({channel:'rail-scene-v2',action:'takeover'},location.origin);
  }
 }
 function beginEntrance() {
  const materials=new Set(),points=[],edgeCache=new Map(),v=new THREE.Vector3();
  root.updateMatrixWorld(true);
  root.traverse(object=>{
   if(!object.isMesh) return;
   (Array.isArray(object.material)?object.material:[object.material]).forEach(m=>materials.add(m));
   // Outline only structural box meshes. Repeated sleepers, foliage and sign planes are omitted.
   if(object.isInstancedMesh||object.geometry.type!=='BoxGeometry') return;
   let edges=edgeCache.get(object.geometry);
   if(!edges){edges=new THREE.EdgesGeometry(object.geometry,30);edgeCache.set(object.geometry,edges);}
   const positions=edges.getAttribute('position');
   for(let i=0;i<positions.count;i++) {v.fromBufferAttribute(positions,i).applyMatrix4(object.matrixWorld);points.push(v.x,v.y,v.z);}
  });
  edgeCache.forEach(g=>g.dispose());
  const geometry=new THREE.BufferGeometry();
  geometry.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
  outline=new THREE.LineSegments(geometry,new THREE.LineBasicMaterial({color:0x91c5ea,transparent:true,opacity:.6,depthWrite:false}));
  scene.add(outline);
  materialStates=[...materials].map(m=>[m,m.onBeforeCompile,m.customProgramCacheKey]);
  for(const [material,compile,cacheKey] of materialStates){
   material.onBeforeCompile=function(shader,renderer){
    compile.call(this,shader,renderer);
    shader.uniforms.railSolidProgress=solidProgress;
    shader.fragmentShader='uniform float railSolidProgress;\n'+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <opaque_fragment>',
     'outgoingLight=mix(vec3(.035,.055,.066),outgoingLight,railSolidProgress);\n#include <opaque_fragment>');
   };
   material.customProgramCacheKey=function(){return cacheKey.call(this)+'-rail-entrance';};
   material.needsUpdate=true;
  }
  root.visible=false;shadowGround.material.opacity=0;
  entranceStart=performance.now();stage.dataset.entrance='running';
  camera.position.set(40,35,44);controls.target.set(0,1,0);
 }
 if(fullEntrance) beginEntrance();
 else {stage.dataset.entrance='complete';restoreView();}
 const motionChange=()=>{reduced=motionPreference.matches;if(reduced)finishEntrance(true);};
 motionPreference.addEventListener('change',motionChange);
 function animate(now){raf=requestAnimationFrame(animate);if(document.hidden||now-lastRender<30)return;lastRender=now;
  if(tween){const t=tween.duration?Math.min(1,(now-tween.start)/tween.duration):1,k=1-(1-t)**3;camera.position.lerpVectors(tween.from,tween.to,k);controls.target.lerpVectors(tween.fromTarget,tween.toTarget,k);camera.zoom=THREE.MathUtils.lerp(tween.fromZoom,tween.toZoom,k);camera.updateProjectionMatrix();if(t===1)tween=null;}
  if(entranceStart!==null) {
   const elapsed=now-entranceStart;
   const progress=THREE.MathUtils.clamp((elapsed-entranceTiming.modelDelay)/entranceTiming.model,0,1);
   const k=1-(1-progress)**3;
   root.visible=progress>0;
   solidProgress.value=k;
   guideLayer.style.opacity=String(THREE.MathUtils.clamp((elapsed-entranceTiming.anchors)/entranceTiming.anchorFade,0,1));
   const labelProgress=THREE.MathUtils.clamp((elapsed-entranceTiming.labels)/entranceTiming.labelFade,0,1);
   for(const marker of markers){
    marker.element.style.opacity=String(labelProgress);
    marker.element.style.clipPath='inset(0 '+(12*(1-labelProgress))+'% 0 0)';
   }
   outline.material.opacity=.6*(1-k);
   shadowGround.material.opacity=.30*k;
   const cameraProgress=THREE.MathUtils.clamp(elapsed/entranceTiming.camera,0,1);
   const eased=1-(1-cameraProgress)**3;
   camera.position.set(40-2*eased,35-3*eased,44-2*eased);
   if(elapsed>=entranceTiming.sceneTotal)finishEntrance();
  }
  controls.update();cameraRing.quaternion.copy(camera.quaternion);cameraRing.material.opacity=.7;
  
  layoutMarkers();renderer.render(scene,camera);frame++;
  if(now-lastSave>300){lastSave=now;saveView();}
 }
 raf=requestAnimationFrame(animate);
 window.__prototype={ready:true,state:()=>({roofHidden,coverage:coverage.visible,selected:selected.id,dayFilter,position:camera.position.toArray(),target:controls.target.toArray(),zoom:camera.zoom,frames:frame,calls:renderer.info.render.calls,entrance:stage.dataset.entrance,outline:Boolean(outline),restored:restoredView})};
 window.addEventListener('pagehide',()=>{finishEntrance();saveView();motionPreference.removeEventListener('change',motionChange);cancelAnimationFrame(raf);resizeObserver.disconnect();labelObserver.disconnect();controls.dispose();clearInterval(autoTimer);const geometries=new Set(),materials=new Set();scene.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>materials.add(m));}});materials.forEach(m=>{m.map?.dispose();m.dispose();});geometries.forEach(g=>g.dispose());renderer.dispose();},{once:true});
}
function reportSceneState(action) {
 if (window.parent !== window) window.parent.postMessage({channel:'rail-scene-v2', action,restored:restoredView}, location.origin);
}
initScene().then(() => reportSceneState('ready')).catch(err=>{console.error(err);$('loading').hidden=false;$('loading').textContent='三维预览未能启动，请使用支持 WebGL 的浏览器并开启图形加速。';reportSceneState('error');});
