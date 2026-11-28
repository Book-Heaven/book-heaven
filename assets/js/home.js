/* Homepage: shelf filters, reading matcher and cover slider. */
(function(){
var $=function(i){return document.getElementById(i)};
var bk=document.querySelectorAll("#bks .bk"),chips=document.querySelectorAll(".pills a"),g="",q="";
function ap(){var n=0;bk.forEach(function(e,i){var ok=(!g||e.getAttribute("data-genre").indexOf(g)>-1)&&(!q||e.getAttribute("data-search").indexOf(q)>-1);e.style.display=ok?"":"none";if(ok)n++});$("st").textContent=n?"Showing "+n+" book"+(n>1?"s":""):"No books match yet";chips.forEach(function(c){c.classList.toggle("on",c.dataset.g===g)})}
chips.forEach(function(c){c.onclick=function(){g=c.dataset.g;ap()}});
$("q").oninput=function(){q=this.value.trim().toLowerCase();ap()};
$("all").onclick=function(e){e.preventDefault();g=q="";$("q").value="";ap()};
var newIndieBooks=[
 ["He Who Fights with Monsters: Book Eight","Shirtaloon (Travis Deverell)","Fantasy · LitRPG adventure","https://www.amazon.com/dp/B0BBWK3T9T","assets/img/covers/he-who-fights-with-monsters-book-eight.jpg","Get it on Amazon","monster","New discovery"],
 ["The Good Daughter","Karin Slaughter","Psychological thriller · Mystery","https://www.amazon.com/dp/B01N7BJZEA","assets/img/covers/the-good-daughter.jpg","Get it on Amazon","gooddaughter","Editor's pick"],
 ["Journey to Joy: March–September 1872","Ginny Dye","Historical fiction","https://www.amazon.com/dp/B098TZQ5LJ","assets/img/covers/journey-to-joy-march-september-1872.jpg","Get it on Amazon","journey","New discovery"],
 ["Beyond What Is Given","Rebecca Yarros","Contemporary romance","https://www.amazon.com/dp/B013P2ERCG","assets/img/covers/beyond-what-is-given.jpg","Get it on Amazon","beyondgiven","Editor's pick"]
];
var moodBooks=newIndieBooks;
var M=[["Heart-racing",[1]],["Heartfelt",[3,2]],["Magical",[0]],["Epic escape",[0,2]],["Surprise me",null],["My saved","saved"]];
function bookKey(b){return "beyond-pages-book-"+String(b[0]||"book").toLowerCase().replace(/[^a-z0-9]+/g,"-")}
function readCount(key){try{return Number(localStorage.getItem(key)||0)}catch(e){return 0}}
function writeCount(key,value){try{localStorage.setItem(key,String(Math.max(0,value)))}catch(e){}}
function statPair(b){var key=bookKey(b),on=readCount(key+"-liked")===1;
return '<div class="rc-stats"><button type="button" class="rc-like'+(on?' is-liked':'')+'" data-book-key="'+key+'" aria-pressed="'+on+'" onclick="toggleBookLike(this);return false;"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4z"/></svg><span class="rc-like-count">'+(on?'Saved':'Save')+'</span></button></div>'}
function toggleBookLike(btn){var key=btn.getAttribute("data-book-key"),on=btn.getAttribute("aria-pressed")==="true";writeCount(key+"-liked",on?0:1);btn.setAttribute("aria-pressed",on?"false":"true");btn.classList.toggle("is-liked",!on);btn.querySelector(".rc-like-count").textContent=on?"Save":"Saved";if(M[cur]&&M[cur][1]==="saved")pick(cur)}
window.toggleBookLike=toggleBookLike;

function card(b){
 var cover=b[4]?'<img src="'+b[4]+'" alt="'+b[0]+' cover" loading="lazy" width="84" height="126">':'<div class="rc-cover '+(b[6]||'')+'" role="img" aria-label="Decorative artwork for '+b[0]+'"><span>'+b[0]+'</span><small>'+b[1]+'</small></div>';
 var link=b[3]||"#";
 return '<article class="rc">'+
 '<a class="rc-cover-link" href="'+link+'" target="_blank" rel="noopener sponsored" aria-label="Open '+b[0]+' on Amazon">'+cover+'</a>'+
 '<div class="rc-info">'+(b[7]?'<span class="eyebrow" style="display:inline-block;margin-bottom:5px">'+b[7]+'</span>':'')+
 '<h3><a class="rc-title-link" href="'+link+'" target="_blank" rel="noopener sponsored">'+b[0]+'</a></h3>'+
 '<p>'+b[1]+' &middot; '+b[2]+'</p>'+statPair(b)+
 '<a class="btn" href="'+link+'" target="_blank" rel="noopener sponsored">'+(b[5]||'Get it on Amazon')+'</a></div></article>';
}
var cur=0;function pick(i){cur=i;var m=M[i][1],h;if(m==="saved"){var s=moodBooks.filter(function(b){return readCount(bookKey(b)+"-liked")===1});h=s.length?s.map(function(b){return card(b)}).join(""):'<p style="color:var(--mute)">Nothing saved yet. Tap Save on any book and it will appear here.</p>'}else{var ix=m||[Math.floor(Math.random()*moodBooks.length)];h=ix.map(function(k){return card(moodBooks[k])}).join("")}$("res").innerHTML=h;document.querySelectorAll("#chips button").forEach(function(c,j){c.classList.toggle("on",j===i)})}
$("chips").innerHTML=M.map(function(m){return '<button type="button">'+m[0]+'</button>'}).join("");
document.querySelectorAll("#chips button").forEach(function(c,i){c.onclick=function(){pick(i)}});pick(0);
var cm=$("cmp"),cL=$("cb"),hd=cm.querySelector(".hd"),dr=false;
function sv(v){v=Math.max(0,Math.min(100,v));cL.style.clipPath="inset(0 "+(100-v)+"% 0 0)";hd.style.left=v+"%";cm.setAttribute("aria-valuenow",Math.round(v))}
function px(e){var r=cm.getBoundingClientRect();sv((e.clientX-r.left)/r.width*100)}
cm.addEventListener("pointerdown",function(e){dr=true;cm.setPointerCapture(e.pointerId);px(e)});
cm.addEventListener("pointermove",function(e){if(dr)px(e)});
cm.addEventListener("pointerup",function(){dr=false});
cm.addEventListener("keydown",function(e){var v=parseFloat(cm.getAttribute("aria-valuenow"));if(e.key==="ArrowLeft")sv(v-5);if(e.key==="ArrowRight")sv(v+5)});
sv(50);
})();
