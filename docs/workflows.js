(function () {

  const D = `
  classDef dir    fill:#0a5c38,stroke:#2cb67d,color:#fff,font-weight:bold
  classDef md     fill:#d4a017,stroke:#a07810,color:#111,font-weight:bold
  classDef script fill:#1e40af,stroke:#3b5fc0,color:#fff
  classDef prompt fill:#c2410c,stroke:#ea580c,color:#fff,font-weight:bold
  classDef output fill:#6d28d9,stroke:#8b5cf6,color:#fff,font-weight:bold`;

  window.WORKFLOWS = [
    {
      id: 'oneshot', navLabel: 'One Shot',
      num: 'Workflow #1', title: 'Specification Driven Design — One Shot',
      desc: 'oneshot.sh validates the specification directory, then concatenates specification files, technology rules, and stack patterns into a single prompt. The AI agent builds the entire application in one pass. Each build is git-tagged — every prototype is fully traceable to the exact specification state that produced it.',
      mermaid: `flowchart LR${D}
  S1["setup.sh"]:::script --> SPEC(["Specifications/"]):::dir
  SPEC --> S2["validate.sh"]:::script --> S3["oneshot.sh"]:::script
  STACK(["Stack/"]):::dir --> S3
  TR(["TechnologyRules/"]):::dir --> S3
  S3 --> PT(["Prompt"]):::prompt
  S3 --> SC{{"SCORECARD.md"}}:::md
  S3 --> GAPS{{"REFERENCE_GAPS.md"}}:::md
  PT --> PT2(["Prototype"]):::output
  PT --> DL{{"deployments.jsonl"}}:::md`,
      learnings: [
        'A well-defined specification file architecture works.',
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
      }
    },
    {
      id: 'iterate', navLabel: 'Iterate',
      num: 'Workflow #2', title: 'Application Iteration',
      desc: 'Changes flow through specifications, not ad-hoc code edits. iterate.sh assembles pending change tickets (SCREEN-NNN-*, FEATURE-NNN-*, PATCH-NNN-*) into a targeted prompt applied to the existing codebase. Once ready, merge.sh squash-merges the prototype branch into a promoted project.',
      mermaid: `flowchart LR${D}
  DL{{"deployments.jsonl"}}:::md --> CH{{"Specification Diff"}}:::md
  CH --> S1["iterate.sh"]:::script
  PT1(["Stack/"]):::dir --> S1
  TR1(["TechnologyRules/"]):::dir --> S1
  S1 --> PT(["Prompt"]):::prompt
  PT --> PT2(["Prototype"]):::output
  S1 --> SC2{{"SCORECARD.md"}}:::md
  PT2 --> S2["merge.sh"]:::script
  PT --> DL2{{"deployments.jsonl"}}:::md
  S2 --> PROJ(["Project"]):::output`,
      learnings: [
        'Updating specifications is far preferable to ad-hoc code edits. The scorecard tracks specification drift over time.'
      ]
    },
    {
      id: 'techrules', navLabel: 'Technology Rules',
      num: 'Workflow #3', title: 'Technology Rules Propagation',
      desc: 'BUSINESS_RULES.md is the source of truth for agent behavior. summarize_rules.sh generates a compact CLAUDE_RULES.md that is injected into every project via ProjectUpdate.sh. All projects share the same behavioral contract, making them interoperable and consistently structured. ProjectValidate.sh verifies compliance.',
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
      ]
    },
    {
      id: 'speciterate', navLabel: 'Self Iteration',
      num: 'Workflow #4', title: 'Automated Specification Iteration',
      desc: 'spec_iterate.sh uses AI to score specification quality across seven dimensions, identify 1–2 highest-priority gaps, and generate a focused iteration prompt. REFERENCE_GAPS.md and SPEC_SCORECARD.md are updated automatically, closing the loop between specification quality and build quality without manual review.',
      mermaid: `flowchart LR${D}
  GAPS{{"REFERENCE_GAPS.md"}}:::md --> SI["spec_iterate.sh"]:::script
  SPEC(["Specifications/"]):::dir  --> SI
  SI --> SCORE{{"SCORECARD.md"}}:::md
  SI --> PROMPT(["Prompt"]):::prompt
  PROMPT --> DL{{"deployments.jsonl"}}:::md
  PROMPT --> Proto(["Prototype"]):::output`,
      learnings: [
        'Works well — one gap at a time, best practices, low-touch review needed.'
      ]
    },
    {
      id: 'tran', navLabel: 'Transaction Logs',
      num: 'Workflow #5', title: 'Capturing Claude Edit Sessions',
      desc: 'Claude edit sessions for diagnostics and feature changes are automatically captured for updates to your specifications. tran_logger.sh reads the Claude session JSONL and git history, then converts them into numbered specification tickets — PATCH-NNN-* for feature changes and AC-NNN-* for acceptance criteria. Numbered files apply in order, giving reproducible build patterns and the ability to work backwards from code to specification.',
      mermaid: `flowchart LR${D}
  DL{{"deployments.jsonl"}}:::md --> TL["tran_logger.sh"]:::script
  PT([".claude JSONL"]):::dir --> TL
  GI(["git logs"]):::dir --> TL
  TL --> SPEC(["Specifications/"]):::dir`,
      learnings: [
        'Requires prompting the agent to produce acceptance criteria alongside feature changes.',
        'Numbered PATCH-NNN-* and AC-NNN-* files give the best reproducible build patterns.'
      ]
    },
    {
      id: 'decompose', navLabel: 'Decompose',
      num: 'Workflow #6', title: 'Reverse-Engineering Existing Applications',
      desc: 'decompose.sh reads an existing project\'s source code, detects the technology stack, and generates an AI prompt that produces structured specification files — METADATA, ARCHITECTURE, DATABASE, SCREEN-*, FEATURE-*, and more. The output feeds directly into Workflow #1, bringing unspecified applications under specification control.',
      mermaid: `flowchart LR${D}
  PROJ(["Existing Project"]):::dir --> D["decompose.sh"]:::script
  TR(["TechnologyRules/"]):::dir --> D
  D --> PT(["Prompt"]):::prompt
  PT --> SPEC(["Specifications/"]):::dir
  SPEC --> WF1(["Workflow #1 →"]):::output`,
      learnings: [
        'Effective for bringing existing applications under specification control without a full rewrite.',
        'Stack detection (Flask, SQLite, Bootstrap) scopes the relevant technology rules automatically.'
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

  /** Render workflow block without I/O columns — for white-paper and summary views. */
  window.renderWorkflowCompact = function (wf) {
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
    return h + `</div>`;
  };

  window.renderAllWorkflowsCompact = function (container) {
    container.innerHTML = window.WORKFLOWS.map((wf, i) =>
      (i > 0 ? '<hr class="wp-div">' : '') + window.renderWorkflowCompact(wf)
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
