/* Three-depth winter snowfall with wind, sway and slow rotation. */
(function(){
 if(window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches)return;
 var canvas=document.createElement("canvas");
 canvas.id="bh-winter-snow";
 canvas.setAttribute("aria-hidden","true");
 canvas.style.pointerEvents="none";
 document.body.insertBefore(canvas,document.body.firstChild);
 var ctx=canvas.getContext("2d"),w=0,h=0,dpr=1,flakes=[],last=0,t=0;
 var layers=[
  {count:34,size:[.7,1.5],speed:[.18,.38],alpha:[.12,.28],sway:.22,wind:.24},
  {count:27,size:[1.2,2.5],speed:[.38,.72],alpha:[.22,.48],sway:.42,wind:.42},
  {count:18,size:[2,3.7],speed:[.65,1.05],alpha:[.3,.62],sway:.65,wind:.68}
 ];
 function rand(a,b){return a+Math.random()*(b-a)}
 function resize(){
  dpr=Math.min(window.devicePixelRatio||1,2);w=window.innerWidth;h=window.innerHeight;
  canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);
  canvas.style.width=w+"px";canvas.style.height=h+"px";
  ctx.setTransform(dpr,0,0,dpr,0,0);
 }
 function addFlakes(){
  flakes=[];
  layers.forEach(function(L,layer){
   for(var i=0;i<L.count;i++)flakes.push({layer:layer,x:rand(0,w),y:rand(0,h),r:rand(L.size[0],L.size[1]),v:rand(L.speed[0],L.speed[1]),a:rand(L.alpha[0],L.alpha[1]),phase:rand(0,Math.PI*2),rot:rand(0,Math.PI*2),spin:rand(-.002,.002),drift:rand(-.18,.18)});
  });
 }
 function frame(now){
  if(!last)last=now;var dt=Math.min((now-last)/16.67,2);last=now;t+=dt;
  ctx.clearRect(0,0,w,h);
  var wind=Math.sin(t*.0022)*.32+Math.sin(t*.0008)*.24;
  flakes.forEach(function(f){
   var L=layers[f.layer],sway=Math.sin(t*.012+f.phase)*L.sway;
   f.x+=(wind*L.wind+f.drift+sway*.12)*dt;
   f.y+=f.v*dt;f.rot+=f.spin*dt;
   if(f.y>h+8){f.y=-8;f.x=rand(0,w)}
   if(f.x>w+8)f.x=-8;if(f.x< -8)f.x=w+8;
   ctx.save();ctx.translate(f.x+Math.sin(t*.004+f.phase)*L.sway*2,f.y);ctx.rotate(f.rot);
   ctx.globalAlpha=f.a;ctx.fillStyle="#f4f7fb";ctx.beginPath();ctx.arc(0,0,f.r,0,Math.PI*2);ctx.fill();ctx.restore();
  });
  requestAnimationFrame(frame);
 }
 window.addEventListener("resize",function(){resize();addFlakes()},{passive:true});
 resize();addFlakes();requestAnimationFrame(frame);
})();
