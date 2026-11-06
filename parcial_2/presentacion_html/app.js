const slides=[...document.querySelectorAll('.slide')];
const toc=document.querySelector('#toc');
const sidebar=document.querySelector('#sidebar');
const scrim=document.querySelector('#scrim');
let current=Math.max(0,Math.min(slides.length-1,Number(location.hash.slice(1)||1)-1));

slides.forEach((slide,index)=>{
  const button=document.createElement('button');
  button.textContent=`${String(index+1).padStart(2,'0')} · ${slide.dataset.title}`;
  button.addEventListener('click',()=>{show(index);closeMenu()});
  toc.append(button);
});

function show(index){
  current=(index+slides.length)%slides.length;
  slides.forEach((slide,i)=>slide.classList.toggle('active',i===current));
  [...toc.children].forEach((item,i)=>item.classList.toggle('active',i===current));
  document.querySelector('#counter').textContent=`${current+1} / ${slides.length}`;
  document.querySelector('#progressBar').style.width=`${((current+1)/slides.length)*100}%`;
  history.replaceState(null,'',`#${current+1}`);
  document.title=`${slides[current].dataset.title} · Parcial 3`;
}
function openMenu(){sidebar.classList.add('open');scrim.classList.add('open')}
function closeMenu(){sidebar.classList.remove('open');scrim.classList.remove('open')}
document.querySelector('#prevBtn').onclick=()=>show(current-1);
document.querySelector('#nextBtn').onclick=()=>show(current+1);
document.querySelector('#menuBtn').onclick=openMenu;
document.querySelector('#closeBtn').onclick=closeMenu;
scrim.onclick=closeMenu;
document.querySelector('#notesBtn').onclick=(event)=>{
  const state=document.body.classList.toggle('show-notes');
  event.currentTarget.setAttribute('aria-pressed',String(state));
};
document.querySelector('#fullBtn').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
document.addEventListener('keydown',event=>{
  if(['ArrowRight','PageDown',' '].includes(event.key)){event.preventDefault();show(current+1)}
  if(['ArrowLeft','PageUp'].includes(event.key)){event.preventDefault();show(current-1)}
  if(event.key==='Home')show(0);
  if(event.key==='End')show(slides.length-1);
  if(event.key==='Escape')closeMenu();
});
show(current);
