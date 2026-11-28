/* Shared behaviour: header, theme, menu, motion and forms. */
window.BH_FORM={endpoint:"https://formsubmit.co/ajax/adscalegrowth@gmail.com",accessKey:""};
(function(){
var $=function(i){return document.getElementById(i)};
var R=document.documentElement,nb=document.querySelector(".navbar"),pg=$("pg");
function sc(){var y=scrollY,h=R.scrollHeight-innerHeight;nb.classList.toggle("s",y>8);pg.style.width=(h>0?y/h*100:0)+"%"}
addEventListener("scroll",sc,{passive:true});sc();
$("th").onclick=function(){var d=R.getAttribute("data-theme")||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");d=d==="dark"?"light":"dark";R.setAttribute("data-theme",d);try{localStorage.setItem("bh-theme",d)}catch(e){}};
if("IntersectionObserver" in window&&!matchMedia("(prefers-reduced-motion:reduce)").matches){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add("in");io.unobserve(e.target)}})},{threshold:.1});document.querySelectorAll("section .wrap,.hero>div").forEach(function(e){e.classList.add("rv");io.observe(e)})}
var E=/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
function fReady(){var c=window.BH_FORM||{};return !!c.endpoint&&(c.endpoint.indexOf("web3forms")<0||!!c.accessKey)}
function fSend(d,cb){if(!fReady()){cb("off");return}var c=window.BH_FORM,b=Object.assign({},d);if(c.accessKey)b.access_key=c.accessKey;
fetch(c.endpoint,{method:"POST",headers:{"Content-Type":"application/json",Accept:"application/json"},body:JSON.stringify(b)}).then(function(r){return r.json().catch(function(){return{}}).then(function(j){var m=String(j.message||"").toLowerCase();if(m.indexOf("activation")>=0||m.indexOf("activate")>=0){cb("activate");return}cb(r.ok&&(j.success===true||j.success==="true")?"ok":"err")})}).catch(function(){cb("err")})}
document.addEventListener("submit",function(e){var sf=e.target;if(sf.id!=="sf")return;e.preventDefault();var o=document.getElementById("sf-out"),b=document.getElementById("sf-btn");o.className="out err";
if(sf.elements._gotcha.value)return;
if(!E.test(sf.elements.email.value.trim())){o.textContent="Enter a valid email address, for example name@example.com.";return}
if(!sf.elements.book_title.value.trim()){o.textContent="Enter the title of your book.";return}
b.disabled=true;o.className="out";o.textContent="Sending...";
fSend({subject:"Book Heaven submission",from_name:sf.elements.name.value,name:sf.elements.name.value,email:sf.elements.email.value,book_title:sf.elements.book_title.value,book_link:sf.elements.book_link.value,message:sf.elements.message.value},function(r){b.disabled=false;
if(r==="ok"){o.className="out ok";o.textContent="Thank you. Your submission has been sent.";sf.reset()}
else if(r==="off"){o.className="out err";o.textContent="Submissions are not switched on yet. Please check back soon."}
else if(r==="activate"){o.className="out err";o.textContent="Please check adscalegrowth@gmail.com and confirm the FormSubmit activation email before submissions can be delivered."}
else{o.className="out err";o.textContent="Something went wrong and your submission was not sent. Please try again."}})});
document.querySelectorAll("form[data-news]").forEach(function(f){f.addEventListener("submit",function(e){e.preventDefault();var i=f.querySelector("input[type=email]"),b=f.querySelector("button");
if(!E.test(i.value.trim())){b.textContent="Check email";setTimeout(function(){b.textContent=f.className==="cf"?"Join the circle":"Subscribe"},2000);return}
b.disabled=true;b.textContent="Sending...";
fSend({subject:"Book Heaven newsletter signup",email:i.value.trim()},function(r){b.disabled=false;
if(r==="ok"){b.textContent="You're on the list";b.disabled=true;i.value=""}
else if(r==="off"){b.textContent="Coming soon"}
else if(r==="activate"){b.textContent="Check inbox to activate"}
else{b.textContent="Try again"}})})});
(function(){var p=document.createElement("div");p.id="prog";document.body.appendChild(p);
function u(){var h=document.documentElement.scrollHeight-innerHeight;p.style.width=(h>0?Math.min(100,scrollY/h*100):0)+"%"}
addEventListener("scroll",u,{passive:true});u();
if(matchMedia("(prefers-reduced-motion:no-preference) and (hover:hover)").matches){
document.addEventListener("pointermove",function(e){var c=e.target.closest&&e.target.closest(".bk .cover");if(!c)return;var r=c.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;c.style.setProperty("--ry",(x*10).toFixed(1)+"deg");c.style.setProperty("--rx",(-y*10).toFixed(1)+"deg")});
document.addEventListener("pointerout",function(e){var c=e.target.closest&&e.target.closest(".bk .cover");if(c){c.style.setProperty("--rx","0deg");c.style.setProperty("--ry","0deg")}})}})();
document.getElementById("bu").onclick=function(){var u=document.querySelector("nav ul"),o=u.classList.toggle("open");this.setAttribute("aria-expanded",String(o))};
document.querySelectorAll("nav ul a").forEach(function(a){a.addEventListener("click",function(){document.querySelector("nav ul").classList.remove("open")})});
})();
/* Books page: category filter. */
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest("#pcat a");if(!a)return;e.preventDefault();
var re=new RegExp(a.getAttribute("data-pg")||".","i");
document.querySelectorAll("#pcat a").forEach(function(x){x.classList.toggle("on",x===a)});
document.querySelectorAll("#pbk .bk").forEach(function(t){t.style.display=re.test(t.getAttribute("data-genre"))?"":"none"})});
