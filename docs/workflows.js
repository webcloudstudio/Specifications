(function () {

  const D = `
  classDef dir    fill:#0a5c38,stroke:#2cb67d,color:#fff,font-weight:bold
  classDef md     fill:#d4a017,stroke:#a07810,color:#111,font-weight:bold
  classDef script fill:#1e40af,stroke:#3b5fc0,color:#fff
  classDef output fill:#6d28d9,stroke:#8b5cf6,color:#fff,font-weight:bold`;

  window.WORKFLOWS = [
    {
      id: 'oneshot', navLabel: 'One Shot',
      num: 'Workflow #1', title: 'Specification Driven Design — One Shot',
      desc: 'Structured specification files and opinionated stack patterns produce a single AI build prompt. Git-tagged for traceability.',
      mermaid: `flowchart LR${D}
  S0["decompose.sh"]:::script --> SPEC(["Specifications/"]):::dir
  S1["setup.sh"]:::script --> SPEC
  SPEC --> S2["validate.sh"]:::script --> S3["oneshot.sh"]:::script
  STACK(["Stack/"]):::dir --> S3
  TR(["TechnologyRules/"]):::dir --> S3
  S3 --> PT(["Prompt"]):::output
  S3 --> SC{{"SCORECARD.md"}}:::md
  S3 --> GAPS{{"REFERENCE_GAPS.md"}}:::md
  PT --> PT2(["Prototype"]):::output
  PT --> DL{{"deployments.jsonl"}}:::md`,
      learnings: [
        'A well defined specification file architecture works.',
        'Opinionated stack — prescriptive patterns, not guidelines.',
        'Scorecards and gap analysis provide directionality.'
      ],
      defn: {
        label: 'Specifications/',
        items: [
          ['METADATA.md', 'Service catalog entry'],
          ['INTENT.md', 'High impact on quality'],
          ['DATABASE.md', 'Core persistence — data first'],
          ['UI-GENERAL.md / SCREEN-*.md', 'UI defined separate from features'],
          ['FUNCTIONALITY.md / FEATURE-*.md', 'Feature definitions'],
          ['SCREEN-NNN-*.md / PATCH-NNN-*.md / AC-NNN-*.md', 'Typed tickets applied in order']
        ]
      },
      io: {
        inputs: ['Specifications/', 'Stack/', 'TechnologyRules/'],
        outputs: ['Prompt', 'Prototype', 'SCORECARD.md', 'REFERENCE_GAPS.md', 'deployments.jsonl']
      }
    },
    {
      id: 'iterate', navLabel: 'Iterate',
      num: 'Workflow #2', title: 'Application Iteration',
      desc: 'Specification changes flow to prototypes as targeted iteration prompts. Promotion squash-merges to projects.',
      mermaid: `flowchart LR${D}
  DL{{"deployments.jsonl"}}:::md --> CH{{"Specification Diff"}}:::md
  CH --> S1["iterate.sh"]:::script
  PT1(["Stack/"]):::dir --> S1
  TR1(["TechnologyRules/"]):::dir --> S1
  S1 --> PT(["Prompt"]):::output
  PT --> PT2(["Prototype"]):::output
  S1 --> SC2{{"SCORECARD.md"}}:::md
  PT2 --> S2["merge.sh"]:::script
  PT --> DL2{{"deployments.jsonl"}}:::md
  S2 --> PROJ(["Project"]):::output`,
      learnings: [
        'Updating specifications much preferred over ad-hoc code edits. Scorecard tracks specification drift.'
      ],
      io: {
        inputs: ['deployments.jsonl', 'Stack/', 'TechnologyRules/'],
        outputs: ['Prompt', 'Prototype', 'SCORECARD.md', 'deployments.jsonl', 'Project']
      }
    },
    {
      id: 'techrules', navLabel: 'Technology Rules',
      num: 'Workflow #3', title: 'Technology Rules Propagation',
      desc: 'Business rules are AI-summarized into CLAUDE_RULES.md and injected into every project, enabling inter-project compatibility.',
      mermaid: `flowchart LR${D}
  RULES(["Technology Rules"]):::dir
  --> S1["summarize_rules.sh"]:::script
  --> CR{{"CLAUDE_RULES.md"}}:::md
  --> S2["ProjectUpdate.sh"]:::script
  --> PROJ(["Project"]):::output
  --> S3["ProjectValidate.sh"]:::script
  --> KPI{{"SCORECARD.md"}}:::md`,
      learnings: [
        'CLAUDE_RULES injection works well out of the box — key insight: use a crafted AI summary.',
        'An opinionated prescribed stack gave working software first time.'
      ],
      io: {
        inputs: ['TechnologyRules/'],
        outputs: ['CLAUDE_RULES.md', 'Project AGENTS.md (injected)']
      }
    },
    {
      id: 'speciterate', navLabel: 'Self Iteration',
      num: 'Workflow #4', title: 'Automated Specification Iteration',
      desc: 'AI-scored gap analysis prioritises 1–2 features, completes specifications, and feeds them back into the build pipeline.',
      mermaid: `flowchart LR${D}
  GAPS{{"REFERENCE_GAPS.md"}}:::md --> SI["spec_iterate.sh"]:::script
  SPEC(["Specifications/"]):::dir  --> SI
  SI --> SCORE{{"SCORECARD.md"}}:::md
  SI --> PROMPT(["Prompt"]):::output
  PROMPT --> DL{{"deployments.jsonl"}}:::md
  PROMPT --> Proto(["Prototype"]):::output`,
      learnings: [
        'Works well — one gap at a time, best practices, low-touch review needed.'
      ],
      io: {
        inputs: ['Specifications/', 'BUSINESS_RULES.md'],
        outputs: ['SPEC_SCORECARD.md', 'SPEC_ITERATION.md', 'REFERENCE_GAPS.md (updated)']
      }
    },
    {
      id: 'tran', navLabel: 'Transaction Logs',
      num: 'Workflow #5', title: 'Capturing Claude Edit Sessions',
      desc: 'Transform Claude internal session logs into formal specification tickets and acceptance criteria.',
      mermaid: `flowchart LR${D}
  DL{{"deployments.jsonl"}}:::md --> TL["tran_logger.sh"]:::script
  PT([".claude JSONL"]):::dir --> TL
  GI(["git logs"]):::dir --> TL
  TL --> SPEC(["Specifications/"]):::dir`,
      learnings: [
        'Requires prompt to create acceptance criteria as well as feature changes.',
        'Approach yielded to specification driven design — used selectively now.'
      ],
      ioCols: [
        { h4: 'Specifications', items: ['PATCH-NNN-tl-*.md', 'AC-NNN-tl-*.md'] }
      ]
    }
  ];

  // ── Shared renderer ─────────────────────────────────────────────────────
  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  /** Render diagram only — no learnings, no I/O, no definitions. */
  window.renderWorkflowDiagram = function (wf) {
    return `<div class="wp-diagram"><div class="mermaid">${wf.mermaid}</div></div>`;
  };

  /** Render full workflow block with all sections. */
  window.renderWorkflow = function (wf) {
    let h = `
<div class="wp-wf">
  <div class="wp-num">${esc(wf.num)}</div>
  <h2 class="wp-title">${esc(wf.title)}</h2>
  <p class="wp-desc">${esc(wf.desc)}</p>
  <div class="wp-diagram"><div class="mermaid">${wf.mermaid}</div></div>`;

    if (wf.learnings && wf.learnings.length) {
      h += `<div class="wp-learn"><div class="wp-learn-lbl">Learnings</div>`;
      wf.learnings.forEach(l => { h += `<p>${esc(l)}</p>`; });
      h += `</div>`;
    }
    if (wf.defn) {
      h += `<div class="wp-defn"><div class="wp-defn-lbl">${esc(wf.defn.label)}</div><ul>`;
      wf.defn.items.forEach(([k, v]) => { h += `<li>${esc(k)}<span> \u2014 ${esc(v)}</span></li>`; });
      h += `</ul></div>`;
    }
    if (wf.io) {
      h += `<div class="wp-io">
        <div class="wp-io-col"><h4>Inputs</h4><ul>${wf.io.inputs.map(i=>`<li>${esc(i)}</li>`).join('')}</ul></div>
        <div class="wp-io-col"><h4>Outputs</h4><ul>${wf.io.outputs.map(i=>`<li>${esc(i)}</li>`).join('')}</ul></div>
      </div>`;
    } else if (wf.ioCols) {
      h += `<div class="wp-io">`;
      wf.ioCols.forEach(col => {
        h += `<div class="wp-io-col"><h4>${esc(col.h4)}</h4><ul>${col.items.map(i=>`<li>${esc(i)}</li>`).join('')}</ul></div>`;
      });
      h += `</div>`;
    }
    return h + `</div>`;
  };

  window.renderAllWorkflows = function (container) {
    container.innerHTML = window.WORKFLOWS.map((wf, i) =>
      (i > 0 ? '<hr class="wp-div">' : '') + window.renderWorkflow(wf)
    ).join('');
    _runMermaid(container);
  };

  window.initWorkflowNav = function (navEl, contentEl) {
    if (navEl.children.length) return; // already init
    navEl.className = 'wf-tab-bar';
    navEl.innerHTML = window.WORKFLOWS.map((wf, i) =>
      `<button class="wf-tab${i===0?' active':''}" data-idx="${i}">${esc(wf.navLabel)}</button>`
    ).join('');

    function show(idx) {
      navEl.querySelectorAll('.wf-tab').forEach((b, i) => b.classList.toggle('active', i === idx));
      contentEl.innerHTML = window.renderWorkflow(window.WORKFLOWS[idx]);
      _runMermaid(contentEl);
    }

    navEl.querySelectorAll('.wf-tab').forEach((btn, i) => btn.addEventListener('click', () => show(i)));
    show(0);
  };

  function _runMermaid(container) {
    if (window.mermaid) {
      const nodes = Array.from(container.querySelectorAll('.mermaid:not([data-processed])'));
      if (nodes.length) window.mermaid.run({ nodes });
    }
  }

  // ── Inject shared CSS once ───────────────────────────────────────────────
  if (!document.getElementById('wp-styles')) {
    const s = document.createElement('style');
    s.id = 'wp-styles';
    s.textContent = `
.wp-wf {}
.wp-num { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:2px; color:#505A68; margin-bottom:6px; }
.wp-title { font-size:22px; font-weight:800; color:#1E2328; margin-bottom:8px; }
.wp-desc { font-size:14px; color:#505A68; margin-bottom:16px; }
.wp-diagram { background:#EAECE8; border:1px solid #D5D8DE; border-radius:6px; padding:18px 14px 10px; margin-bottom:16px; overflow-x:auto; }
.wp-learn { background:#fffbf0; border-left:3px solid #d4a017; border-radius:0 4px 4px 0; padding:12px 16px; margin-bottom:16px; }
.wp-learn-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#b08010; margin-bottom:6px; }
.wp-learn p { font-family:Georgia,serif; font-size:13px; font-style:italic; color:#6b4f00; line-height:1.6; margin:2px 0; }
.wp-defn { background:#f0f5ff; border-left:3px solid #3b82f6; border-radius:0 4px 4px 0; padding:12px 16px; margin-bottom:16px; }
.wp-defn-lbl { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:#3b82f6; margin-bottom:8px; }
.wp-defn ul { list-style:none; padding:0; }
.wp-defn li { font-size:12px; font-family:Consolas,monospace; color:#1e40af; padding:3px 0; border-bottom:1px solid #dbeafe; }
.wp-defn li:last-child { border-bottom:none; }
.wp-defn li::before { content:"· "; color:#3b82f6; }
.wp-defn li span { color:#2E3640; font-family:'Segoe UI',Arial,sans-serif; font-size:12px; }
.wp-io { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px; }
.wp-io-col h4 { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1.2px; color:#2cb67d; margin-bottom:8px; }
.wp-io-col ul { list-style:none; padding:0; }
.wp-io-col li { font-size:12px; font-family:Consolas,monospace; color:#505A68; padding:3px 0; border-bottom:1px solid #D5D8DE; }
.wp-io-col li:last-child { border-bottom:none; }
.wp-io-col li::before { content:"· "; color:#2cb67d; }
.wp-div { border:none; border-top:1px solid #D5D8DE; margin:20px 0; }
.wf-tab-bar { display:flex; gap:6px; margin-bottom:18px; flex-wrap:wrap; padding-bottom:14px; border-bottom:1px solid #D5D8DE; }
.wf-tab { background:#E4E6EA; border:1px solid #D5D8DE; color:#505A68; padding:5px 13px; border-radius:4px; font-size:12px; font-weight:600; cursor:pointer; transition:background .15s,color .15s,border-color .15s; white-space:nowrap; }
.wf-tab:hover { background:rgba(44,182,125,.1); border-color:#2cb67d; color:#1E2328; }
.wf-tab.active { background:rgba(44,182,125,.15); border-color:#2cb67d; color:#2cb67d; }
    `;
    document.head.appendChild(s);
  }

})();
