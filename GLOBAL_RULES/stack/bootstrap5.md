# Bootstrap 5 Best Practices

**Version:** 20260320 V1
**Description:** Bootstrap 5 frontend patterns: layout, components, and form conventions

Technology reference for Bootstrap 5 frontend styling. This file does not change between projects.

Prerequisites: `stack/common.md`

---

## 1. Setup

**Rule**: Load Bootstrap from CDN. Use a single project stylesheet for overrides and custom components.

```html
<!-- In base.html <head> -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-..."
      crossorigin="anonymous">
<link rel="stylesheet" href="/static/css/style.css">
```

```html
<!-- Before </body> -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-..."
        crossorigin="anonymous"></script>
```

Rules:
- CDN for Bootstrap CSS and JS bundle (includes Popper)
- Single `static/css/style.css` for all custom styles
- No build step required — no Sass compilation
- Pin a specific Bootstrap version via CDN URL

**Why**: CDN avoids bundling complexity. Single custom stylesheet keeps overrides organized.

---

## 2. Dark Theme

**Rule**: Use `data-bs-theme="dark"` on `<html>` for Bootstrap's native dark mode. Override with CSS custom properties.

```html
<html data-bs-theme="dark">
```

```css
/* static/css/style.css */
:root {
    --cc-bg: #1a1a2e;
    --cc-surface: #16213e;
    --cc-text: #e0e0e0;
    --cc-border: #2a2a4a;
    --cc-accent: #4fc3f7;
}

body {
    background-color: var(--cc-bg);
    color: var(--cc-text);
}
```

**Why**: Bootstrap 5.3+ has native dark mode. Custom properties let you extend it with project-specific colors.

---

## 3. Layout

**Rule**: Use Bootstrap's container and grid system. Stick to `container` or `container-fluid`.

```html
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">App Name</a>
        </div>
    </nav>

    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
</body>
```

### Grid

```html
<div class="row">
    <div class="col-md-8">Main content</div>
    <div class="col-md-4">Sidebar</div>
</div>
```

Rules:
- Use responsive breakpoints (`col-md-*`, `col-lg-*`)
- `mt-4`, `mb-3`, `p-3` for spacing (Bootstrap utility classes)
- Don't fight the grid — use it or skip it, don't half-use it

---

## 4. Components

**Rule**: Use Bootstrap's built-in components. Style with utility classes first, custom CSS second.

### Cards

```html
<div class="card bg-dark border-secondary">
    <div class="card-header text-uppercase text-muted small">Section Title</div>
    <div class="card-body">
        <p class="card-text">Content here</p>
    </div>
</div>
```

### Tables

```html
<table class="table table-dark table-hover">
    <thead>
        <tr>
            <th>Name</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        {% for item in items %}
        <tr>
            <td>{{ item.name }}</td>
            <td><span class="badge bg-success">Active</span></td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Badges

```html
<span class="badge bg-primary">Primary</span>
<span class="badge bg-success">Active</span>
<span class="badge bg-danger">Error</span>
<span class="badge bg-warning text-dark">Warning</span>
```

### Buttons

```html
<button class="btn btn-sm btn-outline-primary">Action</button>
<button class="btn btn-sm btn-outline-danger">Delete</button>
```

---

## 5. Modals

**Rule**: Use Bootstrap modals for dialogs. For HTMX-loaded content, use custom overlays.

```html
<!-- Bootstrap modal -->
<div class="modal fade" id="confirmModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content bg-dark">
            <div class="modal-header border-secondary">
                <h5 class="modal-title">Confirm</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">Are you sure?</div>
            <div class="modal-footer border-secondary">
                <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button class="btn btn-danger">Confirm</button>
            </div>
        </div>
    </div>
</div>
```

```html
<!-- Custom overlay for dynamic content (HTMX-friendly) -->
<div id="log-overlay" class="position-fixed top-0 start-0 w-100 h-100 d-none"
     style="background: rgba(0,0,0,0.8); z-index: 1050;">
    <div class="container mt-5">
        <pre id="log-content" class="p-3 text-success" style="font-family: monospace;"></pre>
        <button onclick="closeOverlay()" class="btn btn-outline-light mt-2">Close</button>
    </div>
</div>
```

**Why**: Bootstrap modals work for static dialogs. Custom overlays are simpler for HTMX-fetched content.

---

## 6. Custom Component Patterns

**Rule**: Define reusable component classes in your stylesheet using CSS custom properties.

```css
/* Operation buttons — consistent sizing */
.op-btn {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.65rem;
    border-radius: 4px;
    white-space: nowrap;
}

.op-btn--local { background: var(--btn-local, #4fc3f7); color: #000; }
.op-btn--remote { background: var(--btn-remote, #81c784); color: #000; }
.op-btn--danger { background: var(--btn-danger, #ef5350); color: #fff; }

/* Card headers */
.cc-card-header {
    font-size: 0.85rem;
    text-transform: uppercase;
    color: var(--cc-text-muted, #888);
    letter-spacing: 0.05em;
}
```

Rules:
- Use BEM-like naming: `.component--modifier`
- Define colors as CSS custom properties in `:root`
- Keep custom CSS minimal — use Bootstrap utilities first
- Document component classes in a BRANDING.md or style guide

**Why**: Custom properties make theming consistent. BEM naming prevents class collision.

---

## 7. HTMX + Bootstrap Integration

**Rule**: HTMX and Bootstrap coexist without conflict. Use Bootstrap for layout/style, HTMX for behavior.

```html
<!-- HTMX button with Bootstrap styling -->
<button class="btn btn-sm btn-outline-primary op-btn op-btn--local"
        hx-post="/api/project/1/start"
        hx-swap="outerHTML"
        hx-target="closest tr">
    Start
</button>

<!-- HTMX form inside Bootstrap card -->
<div class="card bg-dark border-secondary">
    <div class="card-body">
        <form hx-post="/api/project/1/update" hx-swap="outerHTML">
            <input type="text" class="form-control form-control-sm bg-dark text-light"
                   name="title" value="{{ project.title }}">
        </form>
    </div>
</div>
```

**Why**: Bootstrap handles visual structure. HTMX handles dynamic behavior. No JavaScript framework needed.

---

## Summary Checklist

- [ ] Bootstrap 5.3+ loaded from CDN (CSS + JS bundle)
- [ ] Single `static/css/style.css` for custom styles
- [ ] Dark theme via `data-bs-theme="dark"` + CSS custom properties
- [ ] Container-based layout with responsive grid
- [ ] Standard Bootstrap components (cards, tables, badges, buttons)
- [ ] Custom component classes with BEM naming and CSS variables
- [ ] HTMX attributes on Bootstrap-styled elements
