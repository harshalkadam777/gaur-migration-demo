'use strict';
const $ = id => document.getElementById(id);
let data;
function renderRows() {
  $('records').replaceChildren();
  const events = data.events.filter(e => !$('district').value || e.district === $('district').value);
  $('empty').hidden = events.length !== 0;
  $('empty').textContent = data.events.length ? 'No verified events match this district.' : 'No verified sightings yet. Collected reports require review before publication.';
  for (const event of events) {
    const tr = document.createElement('tr');
    for (const value of [event.observed_on, `${event.district} / ${event.locality}`, event.count ?? 'Unknown']) {
      const td = document.createElement('td'); td.textContent = value; tr.append(td);
    }
    const td = document.createElement('td');
    event.sources.forEach((url, i) => {const a = document.createElement('a'); a.href = url; a.textContent = `Source ${i+1}`; a.target = '_blank'; a.rel = 'noopener noreferrer'; td.append(a);});
    tr.append(td); $('records').append(tr);
  }
}
fetch('data.json', {cache:'no-store'}).then(r => {if (!r.ok) throw new Error('Dataset unavailable'); return r.json();}).then(payload => {
  data = payload;
  const s = data.status;
  const stale = !s.last_success_at || Date.now() - Date.parse(s.last_success_at) > 9*86400000;
  const labels = {never_run:'Collection has not run yet.', not_configured:'No collection sources enabled.', failed:'Collection failed or was incomplete. Previously saved records are retained.', ok:'Configured sources checked successfully.'};
  $('status').textContent = labels[s.state] || 'Collection status unknown.';
  if (s.state === 'ok') $('status').textContent += ` ${s.sources.reduce((n,x)=>n+(x.new||0),0)} new candidate records in the last run.`;
  if (stale) $('status').textContent += ' No recent successful collection is recorded.';
  document.querySelector('.health').classList.toggle('error', stale || s.state !== 'ok');
  $('freshness').textContent = `Last successful check: ${s.last_success_at ? new Date(s.last_success_at).toLocaleString() : 'Never'} · Last attempt: ${s.attempted_at ? new Date(s.attempted_at).toLocaleString() : 'Never'}`;
  $('total').textContent = data.events.length;
  const districts = [...new Set(data.events.map(e=>e.district))].sort();
  $('districts').textContent = districts.length;
  $('pending').textContent = s.candidate_count ?? 0;
  for (const d of districts) {const o=document.createElement('option');o.value=d;o.textContent=d;$('district').append(o);}
  const max = Math.max(1, ...data.weekly.map(w=>w.verified_events));
  data.weekly.forEach((w,i)=>{const col=document.createElement('div');col.className='column';col.title=`Week ${w.week}: ${w.verified_events} verified events; coverage unknown${w.partial ? '; incomplete week' : ''}`;const count=document.createElement('div');count.className='count';count.textContent=w.verified_events || '';const bar=document.createElement('div');bar.className='bar';bar.style.height=`${w.verified_events/max*140}px`;const label=document.createElement('span');label.textContent=i%5===0?w.week.slice(5):'';col.append(count,bar,label);$('chart').append(col);});
  $('built').textContent = `Published dataset built ${new Date(data.built_at).toLocaleString()}`;
  for(const item of data.annual){const card=document.createElement('article');const count=document.createElement('strong');count.textContent=item.verified_events;const year=document.createElement('span');year.textContent=item.year;card.append(count,year);$('annual').append(card);}
  const candidates = data.candidate_records || [];
  const years = {};
  for (const item of [...candidates].sort((a,b)=>(a.observed_on || '').localeCompare(b.observed_on || ''))) {
    const year=(item.observed_on || 'Unknown').slice(0,4); years[year]=(years[year] || 0)+1;
    const tr=document.createElement('tr');
    for (const value of [item.observed_on || 'Unknown', item.id, 'Awaiting review']) {const td=document.createElement('td');td.textContent=value;tr.append(td);}
    const td=document.createElement('td');const link=document.createElement('a');
    if (/^https?:\/\//i.test(item.url || '')) {link.href=item.url;link.textContent=item.source || 'Evidence';link.target='_blank';link.rel='noopener noreferrer';td.append(link);}
    tr.append(td);$('candidateRecords').append(tr);
  }
  $('candidateYears').textContent=Object.entries(years).sort().map(([year,count])=>`${year}: ${count} candidate records`).join(' · ');
  if (!data.events.length) {
    $('chart').replaceChildren();$('chart').textContent='No verified historical series is available yet. See the preserved candidate records below.';
    $('annual').replaceChildren();$('annual').textContent='Historical source data still requires review; annual totals are not established.';
  }
  renderRows();
}).catch(error=>{$('status').textContent='Dashboard data could not be loaded. Please retry later.';document.querySelector('.health').classList.add('error');});
$('district').addEventListener('change',renderRows);
let marathi=false;
$('language').addEventListener('click',()=>{
  marathi=!marathi;document.documentElement.lang=marathi?'mr':'en';$('language').textContent=marathi?'English':'मराठी';
  const labels={heading:['Following the evidence. Understanding the gaur.','पुराव्यांचा मागोवा. गव्यांचा अभ्यास.'],intro:['A living register of verified gaur sightings across Konkan. Every event leads back to its evidence.','कोकणातील पडताळलेल्या गवा दर्शनांची नोंदवही. प्रत्येक घटनेसोबत मूळ पुराव्याचा दुवा.'],statusTitle:['Collection status','माहिती संकलनाची स्थिती'],totalLabel:['Verified events','पडताळलेल्या घटना'],districtLabel:['Districts represented','नोंद असलेले जिल्हे'],candidateLabel:['Collected candidate records','संकलित प्राथमिक नोंदी'],chartTitle:['Reported activity','नोंदवलेली दर्शने'],registerTitle:['Evidence register','पुराव्यांची नोंदवही'],coverage:['Bars count verified events, not animals. Zero means no verified records in this dataset. Observation coverage is unknown; the current week is incomplete.','आलेखात पडताळलेल्या घटना मोजल्या आहेत, प्राणी नाहीत. शून्य म्हणजे या संचात पडताळलेली नोंद नाही. निरीक्षणाची व्याप्ती अज्ञात आहे; चालू आठवडा अपूर्ण आहे.']};
  for(const [id,texts] of Object.entries(labels)) $(id).textContent=texts[marathi?1:0];
});
