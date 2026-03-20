# Create Image

**Version:** 20260320 V1
**Description:** Generate a project card image using AI from an image_description field

Each project can have a card image shown on the Prototyper homepage. The image is generated
by an AI agent from a plain-English description in `METADATA.md`.

---

## Step 1 — Add an Image Description

In your project's `METADATA.md`, fill in the `image_description:` field:

```
image_description: mad scientist with oversized brain, wild hair, green goggles, dark lab
```

Write it the same way you'd prompt an image AI — subject, style details, colors, mood.
One line is enough.

---

## Step 2 — Ask Claude Code to Generate the Image

Open Claude Code in the `Specifications/` directory and ask:

```
Create a card image for <ProjectName> based on the image_description in METADATA.md.
Save it as GAME/static/images/<ProjectName>.webp (400×300px WebP).
Use Pillow to draw it programmatically — cartoon/geometric style.
Add a create_<projectslug>_image() function to GAME/bin/generate_card_images.py.
```

Claude will read the description and write a Pillow drawing function. The result is saved
as a WebP file (400×300px) in the same directory used by all other project card images.

---

## Step 3 — Add the image: field

Once the file is created, add the filename to `METADATA.md`:

```
image: <ProjectName>.webp
```

The Prototyper scanner picks this up on the next refresh and shows it on the homepage card.

---

## Image Spec

| Property | Value |
|----------|-------|
| Format | WebP |
| Size | 400 × 300 px |
| Quality | 85 (WebP) |
| Location | `GAME/static/images/<name>.webp` |
| METADATA field | `image: <name>.webp` |
| Description field | `image_description: <plain English prompt>` |
