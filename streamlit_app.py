"""Optional compatibility viewer; the primary dashboard is served by GitHub Pages."""
import sys
from pathlib import Path
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from observatory import build
st.set_page_config(page_title='Konkan Gaur Observatory',layout='wide')
st.title('Konkan Gaur Observatory / कोकण गवा निरीक्षण')
st.caption('Verified reported sightings; not proof of migration or population estimates.')
try:
    data=build()
except ValueError as exc:
    st.error('Review data failed validation: '+str(exc));st.stop()
st.write('Collection status:',data['status']['state'])
st.write('Last successful check:',data['status']['last_success_at'] or 'Never')
st.metric('Verified events',len(data['events']))
if data['events']:
    st.dataframe(data['events'])
else:
    st.info('No verified sightings yet. Review source evidence before publishing records.')
st.dataframe(data['weekly'])
