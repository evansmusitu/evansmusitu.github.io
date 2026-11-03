#!/usr/bin/env python3
"""MUSITU corporate website: deterministic, dependency-free static builder.
This builds a staging preview only, never touches deployed Intelligence assets.
"""
import json, html, shutil, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
H=lambda s: html.escape(str(s),quote=True)
EVIDENCE_REVIEW_DATE='2026-11-02'
ALLOWED_EXTERNAL_PREFIXES=('https://','mailto:')

# Explicit URL allowlist prevents product data from silently becoming script or data links.
def checked_link_url(url):
    url=str(url)
    if url.startswith('/') and not url.startswith('//'):
        return url
    if url.startswith('#') and len(url)>1:
        return url
    if url.startswith(ALLOWED_EXTERNAL_PREFIXES) and all(ord(c)>=32 for c in url):
        return url
    raise ValueError('Unsupported or unsafe link scheme')


PRODUCTS=[
 dict(slug='axiom',name='MUSITU Axiom',category='Intelligence',maturity='Published integration documented',flag='public',tag='Flagship',line='Structured quantitative work with inspectable inputs and reproducible computation.',summary='Axiom brings deterministic calculations, quantitative workflows and evidence-aware tool use into decision support. Its published ChatGPT integration is reported in the founder portfolio and repository release records; capabilities and access are scoped to the actual approved release.',points=['Quantitative calculation and structured analytical workflows','Inputs, constraints and outputs designed for review','Published ChatGPT integration documented; independently verified release links required at launch'],limits='The broader autonomous operating-system vision, customer accounts, keyless sign-in and integrated billing are not publicly released. Do not infer live trading, financial advice or certified superiority.',proof='GitHub AXIOM release and review record',proof_url='https://github.com/evansmusitu/mft-axiom-build/pull/47',action='Review published AXIOM release',action_url='https://github.com/evansmusitu/mft-axiom-build/pull/47',featured=True),
 dict(slug='education',name='MUSITU Education',category='Education',maturity='Prototype / controlled pilot',flag='prototype',tag='Learning',line='Exploratory learning experiences and controlled educational software.',summary='MUSITU Education brings together learning and revision concepts including ChemForge and Education Nexus. Existing source documents describe offline-first Android development and private institutional controls.',points=['Offline-first educational software experiments','Chemistry revision and interactive learning concepts','Deliberate separation of student app and institutional control plane'],limits='No verified complete accredited curriculum, institutional rollout or qualified production student-data service. Pilot outputs must not be represented as certified assessments.',proof='ChemForge source and release qualification',proof_url='https://github.com/evansmusitu/chemforge-enterprise-android',action='Inspect development record',action_url='https://github.com/evansmusitu/chemforge-enterprise-android'),
 dict(slug='fmi',name='MUSITU Frontier Market Intelligence',category='Markets',maturity='Research / engineering',flag='research',tag='Quantitative research',line='Research-driven market intelligence with explicit safety and execution boundaries.',summary='MUSITU FMI explores quantitative market research, reproducible analytics and controlled execution architectures. Its engineering materials emphasize independent authority, evidence quality and explicit restrictions on live trading.',points=['Research and analytical workflows','Controlled risk and release authority boundaries','Reproducible quantitative validation as an engineering goal'],limits='No authorized live trading, broker execution, certified returns or verified investment performance may be claimed.',proof='FMI research summary — primary records not public',proof_url='/evidence/',action='Read research overview',action_url='/research/'),
 dict(slug='foundry',name='MUSITU Foundry',category='Creative tools',maturity='Prototype / research',flag='prototype',tag='Build and create',line='A frontier for building, reviewing and experimenting with digital products.',summary='Foundry connects product-building ambitions with MUSITU Studio experiments, including experimental 3D interfaces and controlled cloud-rendering studies. Public presentations must separate demonstrated V0.2 results from candidate V0.3 capabilities.',points=['Product ideation and prototyping workflows','Experimental browser-based 3D editing','A documented V0.2 CPU-rendering pilot in private research records'],limits='Do not advertise public commercial 3D SaaS, ready GPU rendering, approved customer storage or completed independent security qualification.',proof='Foundry / Studio summary — primary records not public',proof_url='/evidence/',action='Read research overview',action_url='/research/'),
 dict(slug='markets',name='MUSITU Markets',category='Markets',maturity='Concept / roadmap',flag='research',tag='Opportunity systems',line='Exploring how transparent market information can support useful decisions.',summary='Markets is a canonical MUSITU product family. The proposed scope includes information discovery and future market experiences; certain commerce concepts remain governed drafts rather than public services.',points=['Research into information and opportunity discovery','A possible future home for verified market-facing tools','Explicit separation between research and released commerce'],limits='The Store V2 marketplace is not authorized for live commerce. No checkout, publisher settlement, entitlements or production payments are available here.',proof='Canonical brand policy',proof_url='https://github.com/evansmusitu/mft-axiom-build/blob/main/branding/MUSITU_BRAND_POLICY.md',action='Learn about MUSITU research',action_url='/research/'),
 dict(slug='worldfabric',name='MUSITU WorldFabric',category='Infrastructure',maturity='Concept / research',flag='research',tag='Connected foundations',line='Researching interoperable foundations for more connected digital experiences.',summary='WorldFabric is the canonical family for connected infrastructure and interoperability ambitions. Related work includes MUSITU Connect and early Continuum research, each with its own release qualification.',points=['Interoperability and integrated software systems','Documented Connect runtime and controlled production work','Longer-term connected digital experience research'],limits='Do not represent Continuum as an operational telecommunications network or Connect as generally available commercially without current evidence.',proof='Connect engineering and runtime source',proof_url='https://github.com/evansmusitu/mft-axiom-build',action='Explore Connect source',action_url='https://github.com/evansmusitu/mft-axiom-build')]

PAGES=[
 ('','Home','A company-wide entrance to the MUSITU portfolio, evidence and experiences.','home'),
 ('products','Products','Explore six canonical product families with transparent maturity labels.','products'),
 ('experiences/intelligence','MUSITU Intelligence','Use the existing public AI experience and learn its local-data boundaries.','experience'),
 ('research','Research','The questions, experiments and engineering disciplines behind MUSITU.','research'),
 ('evidence','Evidence','What reproducibility means, what has been tested, and what remains unknown.','evidence'),
 ('company','Company','MUSITU is a Zimbabwe-founded applied AI technology initiative.','company'),
 ('trust','Trust & security','Principles, evidence and honest limitations for responsible technology.','trust'),
 ('resources','Resources','Verified source material, reference documents and development notes.','resources'),
 ('contact','Contact','Connect with MUSITU about evaluation, collaboration and feedback.','contact'),
 ('support','Support','Find the right assistance and understand published product limitations.','support'),
 ('legal/privacy','Privacy','How the preview handles information and what must be reviewed before launch.','privacy'),
 ('legal/terms','Terms','Working terms and limitations; formal legal approval is required before public launch.','terms'),
 ('accessibility','Accessibility','Our accessibility commitments and how the website should be verified.','accessibility'),
 ('404','Page not found','Find your way back to the MUSITU company website.','notfound')]
for p in PRODUCTS:PAGES.append(('products/'+p['slug'],p['name'],p['line'],'product'))
PAGES.extend([('developers','Developers','Technical entry points and engineering resources, gated by product availability.','developers'),('status','Service status','Service monitoring information and its verification boundaries.','status')])
PAGES={path:dict(path=path,title=title,description=description,kind=kind) for path,title,description,kind in PAGES}
assert len(PAGES)==22

SOURCE_LIST=[
 ('Published site','https://evansmusitu.github.io/','Existing MUSITU Intelligence site; current user-facing experience'),
 ('Website source','https://github.com/evansmusitu/evansmusitu.github.io','Existing published source and verification workflows'),
 ('Canonical products','https://github.com/evansmusitu/mft-axiom-build/blob/main/branding/MUSITU_BRAND_CANONICAL.json','Six canonical product families'),
 ('Axiom public-review record','https://github.com/evansmusitu/mft-axiom-build/pull/47','Published version and remaining correction-draft distinction'),
 ('AXIOM customer access hold','https://github.com/evansmusitu/mft-axiom-build/pull/66','Customer identity candidate remains unreleased'),
 ('Education code','https://github.com/evansmusitu/chemforge-enterprise-android','Controlled learning/pilot qualification'),
 ('Store readiness hold','https://github.com/evansmusitu/mft-axiom-build/pull/32','Publisher approval candidate, no marketplace release')]
NAV=[('Products','/products/'),('Research','/research/'),('Evidence','/evidence/'),('Company','/company/'),('Trust','/trust/')]
SITE='MUSITU'
BADGE={'public':'public','prototype':'prototype','research':'research'}

def link(url,label,cls='',external=False):
    url=checked_link_url(url)
    ext=external or url.startswith('https://')
    return f'<a class="{cls}" href="{H(url)}"'+(' target="_blank" rel="noopener noreferrer"' if ext else '')+f'>{H(label)}'+ (' <span aria-hidden="true">↗</span>' if ext else '')+'</a>'

def bstatus(p):return f'<span class="status status--{H(p["flag"])}"><span class="dot" aria-hidden="true"></span>{H(p["maturity"])}</span>'

def card(p, heading_level=3):
    assert heading_level in (2,3)
    return f'''<article class="product-card" data-product-card data-category="{H(p['category'].lower())}" data-state="{H(p['flag'])}" data-search="{H((p['name']+' '+p['category']+' '+p['line']).lower())}">
    <div class="card-top"><span class="index-label">{H(p['tag'])}</span><span class="mini-symbol" aria-hidden="true">✳</span></div>
    <h{heading_level}>{link('/products/'+p['slug']+'/',p['name'])}</h{heading_level}><p>{H(p['line'])}</p>
    <div class="card-bottom">{bstatus(p)}{link('/products/'+p['slug']+'/','Details','quiet-link')}</div><button type="button" class="evidence-trigger" data-evidence="{H(p['slug'])}" aria-haspopup="dialog" aria-label="Review evidence for {H(p['name'])}">Inspect supporting evidence ↗</button></article>'''

def head(title,description,canonical='/'):
    full=f'{title} — MUSITU' if title!='Home' else 'MUSITU — Intelligence with evidence'
    return f'''<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'; frame-src 'none'">
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <meta name="color-scheme" content="dark light">
    <meta name="theme-color" content="#090e1b"><meta name="robots" content="noindex,nofollow"><meta name="description" content="{H(description)}">
    <meta property="og:type" content="website"><meta property="og:title" content="{H(full)}"><meta property="og:description" content="{H(description)}">
    <title>{H(full)}</title><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script defer src="/assets/site.js"></script>
    </head><body><a href="#main" class="skip">Skip to main content</a>'''

def header():
    nav=''.join(link(url,label,'nav-link') for label,url in NAV)
    return f'''<header class="site-header"><div class="shell header-row">
      {link('/','<M> MUSITU','brand')}<nav class="primary-nav" id="primary-nav" aria-label="Main navigation">{nav}</nav>
      <div class="header-actions"><button type="button" class="theme-toggle" id="theme-toggle" aria-label="Switch color theme" title="Switch color theme">◐</button>{link('/experiences/intelligence/','Try Intelligence','button button--small')}
      <button type="button" class="menu-toggle" id="menu-toggle" aria-controls="mobile-nav" aria-expanded="false" aria-label="Open navigation"><span></span><span></span><span></span></button></div></div>
      <nav class="mobile-nav" id="mobile-nav" aria-label="Mobile navigation" hidden>{nav}{link('/experiences/intelligence/','Try Intelligence','nav-link')}</nav>
      </header>'''.replace('&lt;M&gt;','<span class="brand-mark" aria-hidden="true">M</span>')

def footer():
    links=[('Products','/products/'),('Research','/research/'),('Trust','/trust/'),('Support','/support/'),('Privacy','/legal/privacy/'),('Terms','/legal/terms/'),('Accessibility','/accessibility/'),('Contact','/contact/')]
    return f'''<footer class="footer"><div class="shell footer-grid"><div><a class="footer-brand" href="/">✳ MUSITU</a><p>Evidence-aware AI products and research from Zimbabwe.</p><span class="footer-note">Corporate redesign preview · not a new product release.</span></div>
    <nav class="footer-links" aria-label="Footer navigation">{''.join(link(u,t) for t,u in links)}</nav></div>
    <div class="shell footer-bottom"><small>© 2026 MUSITU · Founder-led initiative</small><small>Product maturity and availability vary.</small></div></footer></body></html>'''

def eyebrow(text):return '<span class="eyebrow"><span class="eyebrow-line" aria-hidden="true"></span>'+H(text)+'</span>'
def hero_section(tag,title,description,actions=''):
    return f'<section class="page-hero shell">{eyebrow(tag)}<h1>{title}</h1><p class="lead">{H(description)}</p>{actions}</section>'
def section_title(tag,title,desc=''):
    return f'<div class="section-head">{eyebrow(tag)}<h2>{title}</h2>'+ (f'<p>{H(desc)}</p>' if desc else '')+'</div>'

def evidence_strip():
    return '''<section class="proof-bar"><div class="shell proof-row"><span>Source-linked claims</span><span>Verified maturity labels</span><span>Explicit product limits</span><span>Human-controlled release</span></div></section>'''

def home():
    featured=next(p for p in PRODUCTS if p['featured'])
    return f'''<section class="home-hero shell"><div class="hero-copy">{eyebrow('Evidence-aware technology · Zimbabwe')}<h1>Intelligence <em>with evidence.</em></h1>
    <p class="lead">MUSITU develops applied AI products for quantitative work, responsible automation and connected digital experiences—designed to make important results easier to inspect.</p>
    <div class="hero-actions">{link('/products/axiom/','Explore AXIOM','button button--primary')}{link('/products/','Explore the portfolio','button button--ghost')}</div>
    <p class="microcopy">Independent evaluation matters. Availability differs across products.</p></div>
    <div class="hero-visual" aria-label="Illustration of MUSITU connected product families"><div class="visual-grid"></div><div class="orbit orbit-a"></div><div class="orbit orbit-b"></div><div class="visual-core"><span class="core-mark">✳</span><strong>MUSITU</strong><small>INTELLIGENCE</small></div>
    <span class="orbit-tag tag-a">AXIOM</span><span class="orbit-tag tag-b">EDUCATION</span><span class="orbit-tag tag-c">FOUNDRY</span><span class="orbit-tag tag-d">WORLDFABRIC</span><div class="visual-bottom"><span>Six canonical families</span><span>One accountable identity</span></div></div></section>
    {evidence_strip()}
    <section class="section shell" id="flagship">{section_title('01 / Flagship','Complex questions deserve <span class="accent-text">checkable answers.</span>','Axiom is MUSITU’s primary quantitative-intelligence product. Public release and future development are distinct.')}
    <div class="spotlight"><div><span class="index-label">FLAGSHIP PRODUCT</span><h3>MUSITU Axiom</h3><p>{H(featured['line'])}</p><div class="spotlight-actions">{link('/products/axiom/','Explore the flagship','button button--primary')}{link(featured['proof_url'],'Review release record','text-link',True)}</div></div><div class="spotlight-code" aria-label="Illustrative structured workflow"><div><span>INPUT</span><b>Assumptions + constraints</b></div><div><span>PROCESS</span><b>Deterministic calculations</b></div><div><span>OUTPUT</span><b>Reviewable results</b></div><small>Illustrative workflow, not a live calculation.</small></div></div></section>
    <section class="section section--tint"><div class="shell">{section_title('02 / Product families','Many frontiers. <span class="accent-text">One mission.</span>','Discover the six canonical MUSITU product families, with their development stages visible.')}<div class="card-grid">{''.join(card(p) for p in PRODUCTS)}</div><div class="section-cta">{link('/products/','Explore and filter products','button button--ghost')}</div></div></section>
    <section class="section shell split"><div>{section_title('03 / Working experience','A real place to <span class="accent-text">explore AI.</span>','MUSITU Intelligence already has a published website with an AI interface and bounded local document tooling.')}
    <p>Local-only evidence previews and encrypted browser workspaces require clear privacy explanations. We keep the existing experience in its current origin until safe migration is independently qualified.</p>{link('/experiences/intelligence/','Explore MUSITU Intelligence','button button--primary')}</div><div class="feature-panel"><span class="panel-overline">EXISTING EXPERIENCE</span><div class="feature-screen"><div class="screen-dots"><i></i><i></i><i></i></div><p>Question → bounded analysis → evidence check</p><div class="screen-lines"><span></span><span></span><span></span></div><small>Representation, not a live assistant response</small></div></div></section>
    <section class="section section--tint"><div class="shell">{section_title('04 / Principles','Built to be <span class="accent-text">examined.</span>','A company philosophy that separates what is demonstrated from what is still being researched.')}
    <div class="principle-grid"><article><span>01</span><h3>Evidence over promises</h3><p>Describe real tests and their limitations instead of making unsupported claims.</p></article><article><span>02</span><h3>Control over surprise</h3><p>Important actions should follow explicit permission boundaries.</p></article><article><span>03</span><h3>Research with discipline</h3><p>Prototypes, pilots and production software should never be confused.</p></article></div></div></section>
    <section class="section shell final-cta"><div>{eyebrow('05 / Connect')}<h2>What could we <em>examine together?</em></h2><p>Explore the published technology, inspect the evidence or start a conversation about product fit and collaboration.</p></div><div>{link('/contact/','Start a conversation','button button--primary')}{link('/evidence/','How we evaluate claims','button button--ghost')}</div></section>'''

def products():
    cats=sorted(set(p['category'] for p in PRODUCTS))
    return hero_section('Products / Discover','Explore the <em>portfolio.</em>','Six canonical families. Different kinds of work, different stages of readiness. Filter by focus or maturity without mistaking a research direction for a launched service.')+f'''<section class="section shell"><div class="catalog-controls"><div class="catalog-search"><label for="catalog-query">Search products</label><input id="catalog-query" type="search" placeholder="Find capabilities or products…" autocomplete="off"></div><div class="catalog-filter"><label for="catalog-category">Category</label><select id="catalog-category"><option value="all">All categories</option>{''.join('<option value="'+H(c.lower())+'">'+H(c)+'</option>' for c in cats)}</select></div><div class="catalog-filter"><label for="catalog-state">Stage</label><select id="catalog-state"><option value="all">All stages</option><option value="public">Published</option><option value="prototype">Prototype / pilot</option><option value="research">Research / concept</option></select></div></div><p class="results-count" id="catalog-count" role="status" aria-live="polite">Showing six product families</p><div class="card-grid" id="catalog-grid">{''.join(card(p,2) for p in PRODUCTS)}</div><div class="empty-state" id="catalog-empty" hidden>No products matched. Try a broader search or another category.</div></section>'''

def product_page(p):
    items=''.join('<li>'+H(x)+'</li>' for x in p['points'])
    return hero_section('Products / '+p['category'],H(p['name']).replace('MUSITU ','MUSITU <em>',1)+'</em>',p['line'],link(p['action_url'],p['action'],'button button--primary',p['action_url'].startswith('http')))+f'''<section class="section shell"><div class="product-intro"><div>{eyebrow('Product overview')}<h2>What this work is about.</h2><p>{H(p['summary'])}</p></div><aside class="detail-side"><small>PUBLIC MATURITY STATE</small>{bstatus(p)}<small>PRODUCT FAMILY</small><strong>{H(p['category'])}</strong><small>EVIDENCE</small>{link(p['proof_url'],p['proof'],'text-link',True)}</aside></div></section>
    <section class="section section--tint"><div class="shell narrow">{section_title('Capabilities','What the evidence supports.')}<ul class="feature-list">{items}</ul></div></section><section class="section shell narrow"><div class="notice"><span class="notice-icon">!</span><div><h2>Important limits</h2><p>{H(p['limits'])}</p></div></div><div class="bottom-actions">{link('/evidence/','Read our evidence approach','button button--ghost')}{link('/products/','Back to products','text-link')}</div></section>'''

def editorial(kind):
    d={
 'experience':('Existing live experience','MUSITU Intelligence','A published AI experience with real tools and defined boundaries.',[
 ('The current application','The existing MUSITU Intelligence website includes an AI chat interface, bounded calculations, research routes and browser-local document workflows. Its production setup and stored data should not be altered by this corporate website.'),
 ('Private workspaces','Five opt-in local encrypted browser workspaces are documented. They are not cloud accounts; there is no server-held conversation recovery or automatic cross-device synchronization.'),
 ('Document evidence','Plain-text, Markdown, CSV, JSON, selectable PDF and DOCX workflows process originals locally. Only selected bounded excerpts are sent to the AI service on explicit user action; scanned and encrypted PDFs are unsupported.'),
 ('Source integrity','Local SHA-256 and reproducible excerpt selection can check supplied original bytes. Such receipts do not prove publisher identity, independent fact-checking or a trusted timestamp.')],('Open the existing Intelligence experience','https://evansmusitu.github.io/')),
 'research':('Research / method','Exploration with boundaries','The research program is broader than the set of launched products.',[
 ('Quantitative systems','Research into reproducible calculations, constrained decision workflows and evidence-oriented evaluation.'),('Interoperability','Controlled integration and connected software systems, including MUSITU Connect engineering.'),('Education and creativity','Exploratory software for learning, 3D workflows and experimental interfaces.'),('Publishing discipline','Technical results should include environment, date, measured scope, negative tests and limitations.')],('Review evidence records','/evidence/')),
 'evidence':('Trust / evidence','More proof. Less black box.','A transparent explanation of what a MUSITU claim can and cannot establish.',[
 ('Claim maturity','A public release, a successful isolated test, a private pilot and a research concept are different kinds of evidence.'),('Reproducible calculations','Quantitative examples should retain inputs, algorithms, precision limitations, constraints and exact output checks.'),('Original-source verification','Local file hashes and reproducible excerpts can provide byte-level checks—not independent publication authentication.'),('Independent acceptance','Security qualification and commercial permission require the correct independent authority and provider evidence. Internal tests cannot substitute for them.')],('See source references','#source-register')),
 'company':('Company / identity','Building intelligence with evidence.','MUSITU is a Zimbabwe-founded, founder-led applied AI technology initiative.',[
 ('Who we are','MUSITU develops evidence-aware AI software and research programs. Founder: Evans Musitu. The legal incorporation state and certain commercial qualifications have not been independently established.'),('Why we exist','Important decisions deserve accessible tools, explicit assumptions, controllable actions and reviewable outcomes.'),('One brand, multiple frontiers','The six canonical families are Axiom, Education, Frontier Market Intelligence, Foundry, Markets and WorldFabric.'),('What is next','Mature products through reproducible validation, responsible evaluation and practical customer feedback rather than unsupported superiority claims.')],('Explore our portfolio','/products/')),
 'trust':('Security / disclosure','Trust requires specifics.','Security, privacy and responsible operation should be verifiable, not treated as decoration.',[
 ('Honest release stages','Published experiences and qualified releases are clearly distinguished from prototypes and isolated branches.'),('Data boundaries','The existing AI website uses local document processing and opt-in browser encryption. Bounded selected excerpts can be sent to a remote inference service.'),('Operational control','Privileged operations, customer payments, live trading and tenant identity must remain blocked until their release gates are met.'),('Security claims','MUSITU does not claim independent blanket certification, completed frontier-superiority qualification or unrestricted enterprise-grade deployments.')],('Explore evidence','/evidence/')),
 'resources':('Learn / reference','Research and resources.','Reference materials from public source, not invented case studies or testimonials.',[
 ('Public source','Existing website code and tests document the Intelligence interface and deployment structure.'),('Product evidence','Read the AXIOM release record and source references for the current release distinction.'),('Foundations','Examine the canonical company brand policy and each product’s maturity.'),('Updates','Future announcements should be versioned, dated and reviewed before publication.')],('View sources','#source-register')),
 'contact':('Contact / collaborate','Start a conversation.','For product evaluation, collaboration, research and appropriate business enquiries.',[
 ('Current public route','The existing MUSITU Intelligence website publishes support@mftintelligence.com as a collaboration contact. This address must be owner-verified for the corporate launch.'),('What to include','Identify the relevant product, purpose, organization if applicable and a preferred reply method. Do not send credentials, private financial records or sensitive documents.'),('Response and privacy','A response-time guarantee and contact-form data processing procedure have not been approved; therefore this preview does not submit information to a server.')],('Draft email to published contact','mailto:support@mftintelligence.com?subject=MUSITU%20company%20enquiry')),
 'support':('Support / help','Find the right route.','Clear support boundaries for published experiences and prototype features.',[
 ('Website questions','Use the existing published contact route for website-related feedback until the support destination is formally verified.'),('AXIOM access','Use only the verified published integration and its official help flow; not unreleased customer account candidates.'),('Privacy and local files','The existing encrypted workspaces are browser-local. Losing the passphrase or clearing browser storage can make data unrecoverable.'),('Security reports','Do not send passwords or access tokens by email. A dedicated vulnerability disclosure route requires owner approval.')],('Review product availability','/products/')),
 'privacy':('Legal / working draft','Privacy needs a real policy.','A working preview of privacy disclosures; publication requires lawful review and owner sign-off.',[
 ('Website preview','This static preview deliberately includes no live analytics, tracking pixels, remote fonts, contact-form collection or new customer login.'),('Theme preference','If you choose light or dark mode, only that selection is retained within this browser tab using session storage. It is not transmitted to a server.'),('Linked Intelligence app','The separate live Intelligence experience has its own remote inference interaction and browser-local storage practices. This draft is not a substitute for an approved product-specific privacy notice.'),('Enquiries','The preview does not operate a contact database. Clicking the mail link may open an external email app under that provider’s terms.'),('Final legal review','Before public release: confirm operator identity, lawful basis, data recipients, retention, rights, cross-border processing and applicable Zimbabwean requirements.')],('Contact about privacy','/contact/')),
 'terms':('Legal / working draft','Terms must match reality.','Working terms scope; no legal agreement is made by this preview text.',[
 ('Information and availability','Information is provided for evaluation of a developing portfolio. Products have different readiness states and access controls.'),('No financial advice','Market intelligence, analytical and trading-research content is not a recommendation, promise of returns or authorization for real-money execution.'),('No unsupported warranties','Examples, designs and roadmap descriptions are not guarantees of release or specific service levels.'),('Before public use','Approved business identity, support responsibilities, consumer terms and product-specific agreements require legal review.')],('Read trust principles','/trust/')),
 'accessibility':('Inclusion / access','Accessible by design.','A published accessibility statement should reflect genuine test results.',[
 ('Target','Build to WCAG 2.2 AA with semantic structure, keyboard operation, visible focus, sufficient contrast and reduced motion.'),('Responsive use','Pages are designed for small screens, reflow and common desktop/mobile browsers.'),('Verification','Formal acceptance needs keyboard, screen reader, zoom, contrast and real-device testing. This preview is not a certification.'),('Feedback','A verified accessibility feedback destination should be included before public launch.')],('See support options','/support/')),
 'developers':('Developers / gated','Technical access, explained.','Developer resources should describe only approved and usable interfaces.',[
 ('Currently available','Public repositories and documented integration entry points support technical evaluation.'),('API visibility','Internal Workers, draft customer OAuth, payment and enterprise workspace endpoints must not be advertised as open APIs.'),('Release gate','Publish API reference documentation and credentials only after independent permission and access review.')],('Explore source records','/resources/')),
 'status':('Operations / gated','Operational status.','Service health must come from verified monitoring—not a static green badge.',[
 ('What is confirmed','The existing website repository contains a production-reliability watch workflow with passing bounded checks.'),('What it is not','Passing synthetic checks is not a guarantee that every AI inference or account action works.'),('Public status page gate','Do not publish a live status panel until authoritative monitoring, timestamps, incident process and ownership are established.')],('Explore trust approach','/trust/')),
 'notfound':('Navigation','This page is not here.','The route may have moved or is not included in this preview.',[('Find your way','Try Products, Research, Evidence or Company from the main navigation.')],('Return home','/'))}
    tag,title,desc,items,action=d[kind]
    lis=''.join(f'<article class="info-card"><span class="section-no">{i+1:02}</span><h2>{H(h)}</h2><p>{H(x)}</p></article>' for i,(h,x) in enumerate(items))
    hero=hero_section(tag,H(title).replace('.', '<span class="accent-text">.</span>',1),desc,link(action[1],action[0],'button button--primary',action[1].startswith('http')))
    block=f'<section class="section shell"><div class="info-grid">{lis}</div></section>'
    if kind in ('evidence','resources'):
        block+=f'''<section class="section section--tint" id="source-register"><div class="shell narrow">{section_title('Source register','Inspect original records.','This is a limited public-facing evidence register. Private Drive materials are not published.')}
        <div class="source-list">{''.join('<div><strong>'+H(a)+'</strong><p>'+H(d)+'</p>'+link(u,'Read source','text-link',True)+'</div>' for a,u,d in SOURCE_LIST)}</div></div></section>'''
    if kind in ('privacy','terms','developers','status'):
        block=f'<div class="shell"><div class="notice notice--alert"><span class="notice-icon">!</span><div><h2>Pre-publication gate</h2><p>This page is included in the staging specification and must be reviewed by the appropriate owner before public release. It does not activate a new service or establish final legal terms.</p></div></div></div>'+block
    return hero+block+f'<section class="section shell final-cta compact">{link('/products/','Explore products','button button--ghost')}{link('/contact/','Contact MUSITU','button button--primary')}</section>'

def render(page):
    if page['kind']=='home': content=home()
    elif page['kind']=='products':content=products()
    elif page['kind']=='product':content=product_page(next(p for p in PRODUCTS if page['path']=='products/'+p['slug']))
    else:content=editorial(page['kind'])
    registry=json.dumps({p['slug']:{'name':p['name'],'maturity':p['maturity'],'proof':p['proof'],'url':p['proof_url'],'limits':p['limits'],'reviewed':EVIDENCE_REVIEW_DATE} for p in PRODUCTS},ensure_ascii=False).replace('<','\\u003c')
    drawer=f"""<dialog class=\"evidence-dialog\" id=\"evidence-dialog\" aria-labelledby=\"evidence-title\"><div class=\"dialog-header\"><span class=\"eyebrow\">EVIDENCE RECORD</span><button type=\"button\" id=\"evidence-close\" class=\"dialog-close\" aria-label=\"Close evidence dialog\">×</button></div><h2 id=\"evidence-title\"></h2><p class=\"dialog-label\">CURRENT MATURITY</p><p id=\"evidence-maturity\"></p><p class=\"dialog-label\">WHAT THIS DOES NOT ESTABLISH</p><p id=\"evidence-limits\"></p><p class=\"dialog-label\">SOURCE REVIEW DATE</p><p id=\"evidence-reviewed\"></p><p class=\"dialog-label\">SUPPORTING SOURCE</p><a id=\"evidence-source\" class=\"text-link\" href=\"/evidence/\" rel=\"noopener noreferrer\" target=\"_blank\">Review the public evidence register</a><p class=\"dialog-footnote\">Source records are not a substitute for independent certification.</p></dialog><script type=\"application/json\" id=\"evidence-registry\">{registry}</script>"""
    return head(page['title'],page['description'])+header()+f'<main id=\"main\" tabindex=\"-1\">{content}</main>'+drawer+footer()

def build():
    for product in PRODUCTS:
        assert product['slug'].isalnum(), 'Invalid product slug'
        checked_link_url(product['proof_url'])
        checked_link_url(product['action_url'])
    if DIST.exists():shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST/'assets').mkdir()
    for asset in ('site.css','site.js','favicon.svg'):
        shutil.copy2(ROOT/'assets'/asset,DIST/'assets'/asset)
    for path,page in PAGES.items():
        out=(DIST/path/'index.html') if path else DIST/'index.html'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(render(page),encoding='utf-8')
    # Readable, source-linked public-claim register for staged editorial review.
    register={
      'schema':'musitu.corporate.claim-register.v1',
      'reviewed_on':EVIDENCE_REVIEW_DATE,
      'release_state':'NOINDEX_REVIEW_ONLY',
      'note':'Source review is not a production certification or independent provider acceptance.',
      'families':[{'slug':p['slug'],'name':p['name'],'category':p['category'],
                   'maturity':p['maturity'],'claims':p['points'],'limits':p['limits'],
                   'evidence':{'title':p['proof'],'url':checked_link_url(p['proof_url']),
                               'access':'public_record' if p['proof_url'].startswith('https://') else 'summary_only'}} for p in PRODUCTS]
    }
    (DIST/'claim-register.json').write_text(json.dumps(register,ensure_ascii=False,indent=2),encoding='utf-8')
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n',encoding='utf-8')
    (DIST/'404.html').write_text(render(PAGES['404']),encoding='utf-8')
    manifests=[]
    for f in sorted(DIST.rglob('*')):
        if f.is_file():manifests.append({'path':str(f.relative_to(DIST)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
    (DIST/'build-manifest.json').write_text(json.dumps(manifests,indent=2),encoding='utf-8')
    print(f'Built {len(PAGES)} routes, {len(manifests)} assets and pages; noindex staging preview only.')
if __name__=='__main__':build()
