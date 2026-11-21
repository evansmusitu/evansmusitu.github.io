/* Fail-closed customer enquiry form: prepares a message in the visitor's email app.
   Never claims server-side delivery or silently forwards personal information. */
(() => {
  'use strict';
  const form=document.getElementById('musitu-enquiry-form');
  if (!form) return;
  const status=document.getElementById('enquiry-status');
  form.addEventListener('submit',(event)=>{
    event.preventDefault();
    if (!form.reportValidity()) return;
    const product=form.elements.namedItem('product').value.trim().slice(0,90);
    const purpose=form.elements.namedItem('purpose').value.trim().slice(0,120);
    const email=form.elements.namedItem('email').value.trim().slice(0,254);
    const message=form.elements.namedItem('message').value.trim().slice(0,2500);
    if (!product || !purpose || !email || !message) {
      status.textContent='Please complete all four fields.';return;
    }
    const subject='MUSITU enquiry: '+product+' — '+purpose;
    const body=['Product: '+product,'Purpose: '+purpose,'Reply email: '+email,'','Message:',message].join('\n');
    const href='mailto:support@mftintelligence.com?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
    status.textContent='Email draft prepared. Your email application will open. Press Send there to deliver it; this website has not sent anything.';
    window.location.href=href;
  });
})();
