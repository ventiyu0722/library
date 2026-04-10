#!/usr/bin/env python3
"""Batch evaluation script for all 33 image generation templates.

Generates test images for each template, saves metadata, and supports
scoring for quality assessment.

Usage:
    python eval_templates.py                    # Run all templates
    python eval_templates.py --category A       # Run Category A only
    python eval_templates.py --template A01     # Run single template
    python eval_templates.py --runs 3           # 3 runs per template
    python eval_templates.py --score            # Interactive scoring mode
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from generate import generate_image, get_client, get_model_name

PROJECT_DIR = Path(__file__).parent.parent
RESULTS_DIR = PROJECT_DIR / "test" / "results"
SAMPLES_DIR = PROJECT_DIR / "test" / "samples"

TEMPLATES = {
    "A01": {
        "name": "Chibi Cartoon",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into an adorable chibi-style 3D character. "
            "The character should have an oversized round head (approximately 1:1 head-to-body ratio), "
            "large sparkling anime eyes with highlight reflections, tiny blushing cheeks, and a cheerful smile. "
            "Preserve the subject's exact hairstyle, hair color, and distinguishing facial features for clear identity recognition. "
            "The character wears a miniaturized, stylized version of their original clothing, rendered with soft matte textures "
            "and rounded edges as if sculpted from premium vinyl. Pose: standing with one hand waving, slight head tilt. "
            "Background: clean solid pastel pink gradient. Lighting: soft studio front light with gentle rim highlight. "
            "Render style: high-end 3D chibi figure, glossy eyes, smooth skin shading, subtle ambient occlusion. "
            "No text, no watermark. Aspect ratio 1:1. "
            "The overall style is a premium collectible chibi figure with Pixar-quality rendering and heart-melting kawaii appeal."
        ),
    },
    "A02": {
        "name": "3D Pixar Animation",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a Pixar/Disney-style 3D animated character portrait. "
            "Maintain 100% facial identity accuracy — preserve exact bone structure, jawline, eye shape, nose, hairstyle. "
            "The character has smooth, slightly stylized skin with subtle subsurface scattering, large expressive eyes "
            "with detailed iris reflections. Expression: warm, confident smile with a hint of playfulness. "
            "Outfit: modern casual — clean crew-neck sweater in warm earth tones with soft fabric folds. "
            "Background: soft bokeh gradient in warm golden tones. Lighting: cinematic three-point studio setup — "
            "warm key light from upper-left, cool fill from right, subtle rim light. "
            "Render: ultra-detailed Pixar-quality 3D, global illumination, soft shadows, 8K resolution. "
            "Head-and-shoulders portrait. Aspect ratio 4:5. No text, no watermark. "
            "The overall style is a premium animated movie character portrait with cinematic warmth."
        ),
    },
    "A03": {
        "name": "Comic / Manga",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a stylish manga/comic illustration. "
            "Preserve the subject's facial identity while applying bold comic art stylization. "
            "Style: modern shonen manga with clean linework — strong black ink outlines of varying thickness, "
            "dynamic cross-hatching for shadows, flat color fills with selective gradient shading. "
            "Eyes slightly enlarged and expressive with detailed highlights. Hair has flowing dynamic strands. "
            "Expression: determined and confident, with a slight smirk. "
            "Background: dynamic speed lines radiating from behind with scattered manga-style sparkles. "
            "Halftone dot pattern overlay on background. Head-and-shoulders portrait, slightly low angle. "
            "Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a high-quality manga cover illustration with professional inking and dynamic energy."
        ),
    },
    "A04": {
        "name": "Sketch / Pencil Drawing",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a masterful graphite pencil sketch on textured cream drawing paper. "
            "Preserve the subject's complete facial identity with precise anatomical accuracy. "
            "Technique: realistic academic pencil portraiture using a full tonal range from deep 8B graphite darks "
            "to delicate HB highlights. Employ layered cross-hatching for mid-tones, smooth blending for skin, "
            "crisp directional hatching for hair. Leave strategic areas of bare paper for highlights on forehead and cheekbones. "
            "Three-quarter view head-and-shoulders portrait. Hair rendered with individual strand groupings. "
            "Background: minimal — soft loose gestural strokes fading to blank paper, vignette effect. "
            "Aspect ratio 1:1. No color, no watermark. "
            "The overall style is a museum-quality graphite portrait combining photorealistic accuracy with visible artistic handcraft."
        ),
    },
    "A05": {
        "name": "Clay / Claymation",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a charming claymation-style character. "
            "Preserve key facial features and identity while rendering as hand-sculpted modeling clay. "
            "Smooth rounded clay surfaces with visible hand-molded textures — subtle fingerprint impressions, "
            "gentle surface undulations, soft edges where clay pieces join. Eyes are large expressive spheres. "
            "Hair sculpted from matching-color clay in thick stylized strands. "
            "Outfit: a miniaturized version of the original clothing, crafted from clay with simplified details. "
            "Pose: standing with a friendly wave and tilted head. "
            "Background: simple pastel-colored clay backdrop with soft even studio lighting. "
            "Aspect ratio 1:1. No text, no watermark. "
            "The overall style is a premium Aardman/Laika-quality claymation character with heartwarming tactile appeal."
        ),
    },
    "A06": {
        "name": "80s Retro Animation",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a stylish 1980s retro animation character portrait. "
            "Preserve facial identity while applying 80s cel-animation visual language. "
            "Bold clean cel-animation look with strong black outlines, flat color fills with hard-edged shadow shapes, "
            "vibrant saturated colors. Eyes large and sparkly with multiple highlight reflections. "
            "Hair with dramatic volume and flow, sharp highlight streaks in electric blue. "
            "Outfit: stylish 80s ensemble — oversized pastel blazer with rolled sleeves, geometric-print t-shirt. "
            "Background: synthwave sunset gradient — deep purple through hot magenta to neon orange, chrome grid receding to horizon. "
            "Lens flares and star sparkles. Film grain overlay. "
            "Composition: head-and-shoulders, slightly heroic low angle. Aspect ratio 4:5. No text, no watermark. "
            "The overall style is a premium 80s animation cel portrait blending City Pop aesthetics with synthwave neon drama."
        ),
    },
    "A07": {
        "name": "Retro-Futurism",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a retro-futuristic portrait in the style of 1960s space-age illustration. "
            "Preserve facial identity while placing them in a sleek optimistic vision of the future from the mid-20th century. "
            "Outfit: a streamlined silver space suit with orange accent panels, transparent dome helmet beside them. "
            "Background: sweeping retro-futuristic cityscape — gleaming chrome towers with rounded edges, flying cars with tail-fins, "
            "monorail tracks, a ringed planet on the horizon. Sky transitions from teal to warm coral. "
            "Style: painted illustration with visible brushwork, reminiscent of Syd Mead. Saturated but slightly muted colors. "
            "Three-quarter portrait. Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a premium retro-futuristic painted illustration evoking optimistic 1960s space-age dreams."
        ),
    },
    "A08": {
        "name": "Ukiyo-e / Chinese Painting",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into an exquisite Japanese Ukiyo-e woodblock print portrait. "
            "Preserve facial identity while rendering in traditional art style. "
            "Subject wears an elegant traditional kimono with intricate floral patterns in indigo blue and vermilion red. "
            "Technique: bold hand-carved ink outlines of varying thickness, flat areas of color from traditional mineral pigments "
            "(Prussian blue, vermilion, yellow ochre, soft green), visible wood-grain texture throughout. "
            "Background: stylized clouds, distant mountainscape with Mt. Fuji silhouette, cherry blossom branches framing one side. "
            "Include paper fiber texture, slight pigment bleeding for authenticity, red artist seal stamp in corner. "
            "Portrait from chest up. Aspect ratio 3:4. No modern elements, no watermark. "
            "The overall style is a museum-quality traditional Ukiyo-e portrait with authentic period craftsmanship."
        ),
    },
    "A09": {
        "name": "Watercolor Portrait",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a luminous watercolor portrait on cold-pressed watercolor paper. "
            "Preserve facial identity with artistic interpretation — key features recognizable. "
            "Professional watercolor portraiture with wet-on-wet blending, limited harmonious palette: "
            "warm skin tones from raw sienna and cadmium red; cool shadows in cerulean blue and light violet. "
            "Key effects: visible paper grain through transparent washes, pigment pooling and granulation at edges, "
            "controlled blooms where wet colors merge, dry-brush strokes for hair texture. "
            "White of paper serves as brightest highlights on nose tip and brow ridge. "
            "Background: loose suggestive washes in complementary cool blues fading toward paper edges. "
            "Head-and-shoulders, slightly off-center. Aspect ratio 1:1. No text, no watermark. "
            "The overall style is a gallery-quality watercolor portrait with luminous transparency and spontaneous beauty."
        ),
    },
    "A10": {
        "name": "K-Pop Star",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a stunning K-Pop idol concept photo. "
            "Preserve 100% facial identity while elevating to top-tier K-Pop visual standards. "
            "Flawless dewy glass skin with subtle highlight on cheekbones, soft gradient lip tint in rose pink, "
            "subtle smoky liner and natural lashes. Brows groomed to a clean natural arch. "
            "Hair: styled in fluffy textured layers with center part, in trendy ash brown with subtle highlights. "
            "Outfit: designer oversized blazer in cream white over thin chain necklace and black turtleneck. "
            "Background: clean studio with soft dreamy haze and pastel lens flares. "
            "Lighting: large softbox for flawless skin, subtle cool blue rim light from behind. "
            "Camera: 85mm, f/2.0, slightly desaturated color grading with lifted blacks. "
            "Aspect ratio 3:4. Head-to-waist framing. No text, no watermark. "
            "The overall style is an official K-Pop idol concept photo worthy of a debut album photobook."
        ),
    },
    "A11": {
        "name": "Imperial / Royal",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a grand European Renaissance royal portrait in oil painting style. "
            "Preserve complete facial identity — exact bone structure and features. "
            "Subject wears magnificent crimson velvet royal robes with ermine fur trim, intricate gold embroidery, "
            "and a jewel-encrusted crown. Seated on an ornate gilded throne, one hand resting on armrest, "
            "the other holding a golden scepter. "
            "Background: palatial interior — deep burgundy drapes with gold tassels, marble column partially visible, "
            "warm candlelight illuminating a tapestry with coat of arms. "
            "Technique: rich oil paint with impasto brushwork on highlights, smooth glazing for skin. "
            "Dramatic chiaroscuro — warm golden key light, deep shadows, candlelight reflections on metal. "
            "Three-quarter body portrait. Aspect ratio 3:4. No modern elements, no watermark. "
            "The overall style is a museum-worthy classical royal portrait with old-master painting grandeur."
        ),
    },
    "A12": {
        "name": "90s Yearbook",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform this selfie into a 1990s American high school yearbook photo. "
            "Preserve the subject's complete facial identity. "
            "Classic 90s yearbook portrait — head-and-shoulders framed shot, soft diffused dual-umbrella studio lighting, "
            "gentle catch-lights in eyes. Background: iconic 90s laser-beam gradient — cyan and magenta rays against deep cobalt blue. "
            "Subject wears a navy crew-neck sweater with a plaid button-up collar visible underneath. "
            "Film: Kodak Gold 200 — warm color shift, subtle grain, slightly desaturated reds. "
            "Characteristic 90s soft-focus portrait look. Hair styled naturally, period-appropriate. "
            "Centered subject, tight head-and-shoulders crop with even breathing space. Square format 1:1. "
            "The overall style is an authentic 1990s American high school yearbook photo. No modern elements."
        ),
    },
    "A13": {
        "name": "High Fashion",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a high-fashion editorial portrait. "
            "Preserve facial identity with 100% accuracy while elevating to top-tier fashion magazine standards. "
            "Dramatic editorial makeup — bold sculpted cheekbones, smoky eye with metallic copper accents, matte nude lip. "
            "Hair: sleek sculptural updo with loose face-framing tendrils. "
            "Outfit: avant-garde structured shoulder piece in black with metallic thread detailing, sheer high-neck underlayer. "
            "Lighting: dramatic Vogue-style — hard key light from 45° creating strong shadow geometry, large reflector fill, "
            "deep amber hair light. Camera: 100mm telephoto, f/2.8, razor-thin DOF. "
            "Background: seamless charcoal to black gradient. Rich contrast, deep blacks, slightly warm skin tones. "
            "Tight portrait from chest up. Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a cover-worthy high-fashion editorial with dramatic lighting and commanding presence."
        ),
    },
    "A14": {
        "name": "Cyberpunk Portrait",
        "category": "A",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a stunning cyberpunk portrait. "
            "Preserve facial identity while immersing in a neon-drenched dystopian future. "
            "Subject has sleek chrome cybernetic augmentations — thin LED-lit strip along jawline, "
            "glowing cyan optical implant in one eye, micro-circuit tattoos on neck in bioluminescent blue. "
            "Outfit: weathered black tactical jacket with holographic patches, fiber-optic threading pulsing violet. "
            "Environment: rain-slicked megacity alley — towering buildings with holographic ads, steam from grates, "
            "reflections of pink and cyan neon on wet surfaces. "
            "Lighting: hot magenta from left, electric cyan from right, amber street lamp behind. Rain droplets scatter neon. "
            "Camera: 50mm at f/1.4, subject sharp, background dissolving into neon bokeh circles. "
            "Aspect ratio 9:16 vertical. No text, no watermark. "
            "The overall style is a cinematic cyberpunk portrait blending Blade Runner atmosphere with photo-real quality."
        ),
    },
    "B01": {
        "name": "Studio Photoshoot",
        "category": "B",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a high-end studio portrait photoshoot. "
            "Preserve complete facial identity, expression nuance, and natural skin texture. "
            "Setting: professional photography studio with seamless paper backdrop in warm taupe. "
            "Outfit: elegant camera-ready — tailored blazer in soft camel over a simple white t-shirt. "
            "Pose: natural three-quarter body angle, one shoulder slightly forward, head tilted 10 degrees, relaxed expression. "
            "Lighting: professional three-point — large octabox key light at 45° camera-left, silver reflector fill from right, "
            "subtle strip light for hair separation. 5500K daylight balanced. "
            "Camera: 85mm at f/2.0, shallow DOF, eyes tack-sharp. Film: Fuji Pro 400H — lifted shadows, creamy tones. "
            "Three-quarter body with generous headroom. Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a premium studio portrait with magazine-grade lighting and timeless elegance."
        ),
    },
    "B02": {
        "name": "ID Photo",
        "category": "B",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into a professional ID/passport-style headshot. "
            "Preserve facial identity with absolute accuracy — no alterations to facial features. "
            "Formal head-and-shoulders against a solid white background with no texture or shadows. "
            "Subject faces camera directly with neutral calm expression, mouth closed, eyes open and straight. "
            "Flat even illumination from dual front lights, no shadow on background or under chin. 5500K neutral. "
            "Clean dark-colored formal shirt. Ears visible, forehead clear, no hair covering eyes. "
            "Natural skin — no beauty filter, no smoothing, faithful skin tone. "
            "Head centered, face occupying 70% of vertical space. Aspect ratio 3:4. "
            "The overall style is a regulation-compliant ID photograph with professional studio quality."
        ),
    },
    "B03": {
        "name": "Pet Humanization",
        "category": "B",
        "needs_photo": True,
        "photo_type": "pet",
        "prompt": (
            "Transform the uploaded pet photo into a sophisticated anthropomorphic portrait. "
            "The pet becomes a dignified humanoid character preserving their exact species, breed, fur color/pattern, and expression. "
            "Standing upright in human pose, wearing a tailored three-piece suit in charcoal gray "
            "with burgundy silk pocket square and gold cufflinks. Human-like posture with animal head, fur, ears. "
            "Expression: dignified and slightly amused, as if posing for a corporate headshot. "
            "Background: rich dark wood-paneled study with leather-bound books and warm desk lamp. "
            "Lighting: warm Rembrandt key light from left, fill from right, backlight for fur separation. "
            "Hyper-realistic digital painting with individual fur strands and fabric texture. "
            "Three-quarter body portrait. Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a premium anthropomorphic pet portrait with Victorian gentleman painting elegance."
        ),
    },
    "B04": {
        "name": "Emoji / Sticker Pack",
        "category": "B",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Create a 3x3 grid sticker set (9 stickers) based on the uploaded photo. "
            "Pixar-quality 3D with slightly exaggerated proportions — head slightly larger, big expressive eyes. "
            "Preserve exact hairstyle, hair color, and key facial features across all 9 stickers. "
            "9 expressions: 1.Happy smile 2.Laughing 3.Cool(sunglasses) 4.Surprised(wide eyes,hands on cheeks) "
            "5.Thinking(chin on hand) 6.Winking(tongue out) 7.Heart eyes(heart gesture) 8.Angry(puffed cheeks,steam) 9.Thumbs up. "
            "Each sticker: head-and-shoulders only, different casual outfit, bold clean outline, subtle drop shadow. "
            "White background per cell. Clear spacing between stickers. "
            "Final layout: 3x3 grid, cream background, 1:1 aspect ratio, ultra-high resolution. "
            "The overall style is a premium collectible sticker pack with consistent identity and expressive range. No text labels."
        ),
    },
    "B05": {
        "name": "Avatar / Profile Picture",
        "category": "B",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Transform the uploaded photo into an 8K stylized digital portrait illustration for use as an avatar. "
            "Semi-realistic style blending editorial portrait art with graphic novel aesthetics. "
            "Strong sketch-like linework with expressive strokes, visible textured brushwork and painterly shading, "
            "dry brush effects around shoulders where image softly dissolves. "
            "Face accuracy critical: match 100% — preserve exact facial structure, bone anatomy, grooming details. "
            "Natural skin texture with varied tones. No beautification — preserve raw realism and imperfections. "
            "Background: minimal cream with a bold orange square behind the head for contrast and halo-like framing. "
            "Lighting: soft directional from upper left. "
            "Head-and-shoulders portrait, perfectly centered, shoulders not touching edges. Aspect ratio 1:1. "
            "The overall style is an ultra-detailed premium illustration portrait functioning as a distinctive social media avatar."
        ),
    },
    "C01": {
        "name": "Pet Stylization",
        "category": "C",
        "needs_photo": True,
        "photo_type": "pet",
        "prompt": (
            "Transform the uploaded pet photo into an adorable kawaii needle-felted plush portrait. "
            "Preserve exact breed characteristics, fur color/pattern, eye color, and distinguishing features. "
            "Rendered as soft needle-felted wool — fluffy texture with visible fine stitching and fuzzy edges. "
            "Big sparkling eyes with detailed reflections, tiny blushing cheeks, happy heart-melting smile. "
            "Scene: sitting among colorful flowers, tiny sparkles floating around, warm gentle golden-hour lighting. "
            "Accessories: a tiny flower crown on the head matching the color palette. "
            "Color palette: warm pastels with soft pink, lavender, and mint green accents. "
            "Centered pet portrait. Aspect ratio 1:1. No text, no watermark. "
            "The overall style is a heart-melting kawaii pet portrait with ultra-detailed plush texture and magical warmth."
        ),
    },
    "C02": {
        "name": "Baby Comic Grid",
        "category": "C",
        "needs_photo": True,
        "photo_type": "baby",
        "prompt": (
            "Transform the uploaded baby photo into a delightful 2x2 comic-style grid with four different expressions. "
            "Preserve the baby's exact facial features and skin tone across all four panels. "
            "Vibrant manga/comic aesthetic with bold outlines, bright colors, playful effects. "
            "Panel 1 (top-left, yellow bg): Surprised face — wide eyes, exclamation marks, speed lines. "
            "Panel 2 (top-right, pink bg): Pouty face — puffed cheeks, manga anger veins, small flames. "
            "Panel 3 (bottom-left, blue bg): Laughing — open-mouth giggle, musical notes, sparkle stars. "
            "Panel 4 (bottom-right, green bg): Cute/shy — head tilted, blushing cheeks, floating hearts. "
            "Center intersection: heart-shaped frame with miniature baby waving. "
            "White borders between panels. Baby in different animal-themed onesies per panel. "
            "2x2 grid. Aspect ratio 1:1. "
            "The overall style is a vibrant baby comic page bursting with personality and kawaii charm."
        ),
    },
    "C03": {
        "name": "Pet VOGUE Magazine",
        "category": "C",
        "needs_photo": True,
        "photo_type": "pet",
        "prompt": (
            "Transform the uploaded pet photo into a glamorous fashion magazine cover. "
            "Preserve exact breed, fur color/pattern, and distinctive features. "
            "Pet poses wearing designer sunglasses pushed up on head, draped in luxurious bathrobe, "
            "leaning back on velvet chaise lounge with effortless attitude. "
            'Masthead: large "VOGUE" at top in classic Didot serif font, white with subtle shadow. '
            'Cover lines on left: "THE PET ISSUE", "Best Dressed Fur Babies 2026", "Luxury Life". '
            "Photography: beauty dish lighting from above-right, fill reflector, rim light for fur separation. "
            "Film: Kodak Portra 400 — creamy tones, subtle grain. "
            "Background: luxurious setting with marble floor, velvet drapes, vintage gold frame. "
            "Classic fashion magazine cover layout. Aspect ratio 3:4. "
            'The overall style is a premium high-fashion pet magazine cover. "VOGUE" must be spelled correctly.'
        ),
    },
    "D01": {
        "name": "Outfit Change",
        "category": "D",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "A precise local image edit replacing only the clothing while keeping everything else pixel-identical. "
            "Replace current outfit with a tailored navy blue blazer over a crisp white dress shirt, top button undone. "
            "Fine wool texture with subtle herringbone pattern, natural draping. "
            "Absolute Preservation: face, expression, skin tone, hair, body pose, hand positions, ALL background elements, "
            "camera angle, focal length, color grading, white balance. "
            "Clothing edges blend seamlessly with neck and wrists. Shadows follow existing lighting direction. "
            "Do not change the aspect ratio. Do not alter the face in any way. "
            "The result is a seamless photorealistic outfit swap indistinguishable from an original photograph."
        ),
    },
    "D02": {
        "name": "Hairstyle Change",
        "category": "D",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "A precise local image edit changing only the hairstyle while keeping everything else pixel-identical. "
            "Transform hair to a short textured pixie cut with side-swept bangs in warm honey blonde with darker roots. "
            "Natural movement and texture, individual strand detail, realistic shine matching scene lighting. "
            "Absolute Preservation: face, expression, skin tone, eyebrows, clothing, every fabric detail, ALL background pixels, "
            "camera angle, focal length, color grading. "
            "Hairline blends naturally with forehead and temples. Newly exposed areas match face skin tone. "
            "Do not change the aspect ratio. Do not alter the face. "
            "The result is a seamless photorealistic hairstyle change indistinguishable from an original photograph."
        ),
    },
    "D03": {
        "name": "Background Change",
        "category": "D",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Replace the entire background while keeping the subject completely unchanged. "
            "New background: a serene Japanese zen garden — raked white sand patterns, smooth gray stones, "
            "bamboo water fountain, moss-covered rocks, soft morning mist, warm golden hour sunlight through bamboo groves. "
            "Absolute Preservation: every detail of the subject — face, expression, hair, clothing, pose, accessories, skin tone. "
            "Background has natural depth of field — sharp mid-ground, gentle bokeh further back. "
            "Warm directional sunlight from right. Subject edges have natural anti-aliased quality. "
            "Subject's feet/base connects naturally with new ground surface. Cast shadows on new ground. "
            "Do not change the aspect ratio. "
            "The result is a seamless composite where the subject appears genuinely photographed in the new location."
        ),
    },
    "E01": {
        "name": "Social Media Post",
        "category": "E",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            'Create a visually stunning Instagram quote card. '
            'Main text: "Stay Hungry, Stay Foolish" — large, light-gold elegant serif font, centered, generous letter-spacing. '
            'Attribution: "— Steve Jobs" — smaller text below, same font family. '
            "Large subtle decorative quotation mark watermark behind the text. "
            "Background: rich warm brown gradient, slightly textured like premium paper. "
            "Typography: sharp, perfectly rendered, no misspellings, no text warping. "
            "Clean balanced layout with professional graphic design spacing. Aspect ratio 1:1. "
            "The overall style is a premium social media graphic ready for immediate posting. No watermark."
        ),
    },
    "E02": {
        "name": "Poster Design",
        "category": "E",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            'Create a high-contrast bold graphic design poster for "UC Berkeley Music Society Spring Auditions". '
            'Text to render EXACTLY (letter-perfect, no misspellings): '
            'Hero text (top): "SPRING AUDITIONS" — extra bold sans-serif, all caps, white, largest on poster. '
            'Subtitle: "UC Berkeley Music Society" — medium weight, 60% of title size. '
            'Details: "April 15th • Sproul Hall Room 202 • 6-9 PM" — light weight, smaller. '
            "Color palette: deep navy background, bright coral accents, white text. "
            "Abstract geometric shapes (circles, triangles) in accent colors. Clean modern layout. "
            "Aspect ratio 3:4. "
            "The overall style is a professional print-ready event poster with striking typography. No spelling errors."
        ),
    },
    "E03": {
        "name": "Storyboard / Comic Strip",
        "category": "E",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            "Create a 4-panel horizontal comic strip depicting a day in the life. "
            "4 evenly-spaced panels left-to-right, clean black borders, white gutters. "
            "Panel 1: Character waking up, alarm ringing, messy hair, morning light through window. "
            "Panel 2: Drinking coffee, looking at phone, kitchen setting, warm lighting. "
            "Panel 3: At work desk, focused expression, computer screen glow. "
            "Panel 4: Relaxing at sunset, happy and satisfied, beautiful sky colors. "
            "Art style: clean modern comic illustration with bold outlines, flat colors, cel-shading. "
            "Character identical across all panels — same face, body, hair. "
            "Widescreen storyboard format. Aspect ratio 16:9. "
            "The overall style is a professional storyboard with clear narrative progression and consistent character design."
        ),
    },
    "E04": {
        "name": "Handwritten Poster",
        "category": "E",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            'Create a beautiful hand-drawn educational poster on "Environmental Protection". '
            "Large poster divided into visually distinct sections with hand-drawn borders. "
            "Title at top in large colorful hand-lettered text with decorative doodles. "
            "Sections: Key Facts with small illustrative icons, What We Can Do with checkboxes and doodles, "
            "Did You Know? with a hand-drawn illustration, Our Pledge in a framed statement. "
            "Style: charming hand-drawn with colored markers and crayons on white poster board. "
            "Hand-lettered text (not computer fonts), cute doodles in margins, decorative vine borders. "
            "Bright cheerful palette — red, blue, green, yellow, orange, purple. "
            "Portrait orientation. Aspect ratio 3:4. All text legible. "
            "The overall style is a heartwarming creative class poster that looks genuinely hand-made."
        ),
    },
    "E05": {
        "name": "Illustration",
        "category": "E",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            "Create a stunning Studio Ghibli-inspired watercolor illustration depicting "
            "a young adventurer standing at the edge of a floating island, looking out at a sky filled "
            "with whales swimming among the clouds. "
            "Soft dreamy palette with warm golden undertones, delicate linework beneath transparent washes. "
            "Lush green grass and wildflowers on the floating island, ancient stone ruins with ivy, "
            "clouds at eye level, distant floating islands, gentle sunset in peach and lavender. "
            "Golden hour back-lighting creating warm silhouette effect, god-rays through clouds. "
            "Character at left-third looking right toward expansive sky, creating sense of scale. "
            "Aspect ratio 3:4. No text, no watermark. "
            "The overall style is a breathtaking illustration worthy of a children's book cover with wonder and serenity."
        ),
    },
    "F01": {
        "name": "E-commerce Main Image",
        "category": "F",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            "Ultra-realistic cinematic product shot of a premium honey jar placed inside a shallow wooden hollow "
            "surrounded by tall wild wheat and tiny yellow meadow flowers. Intimate low-angle macro perspective. "
            "Transparent glass jar filled with luminous deep golden honey, satin bronze metallic lid, "
            'narrow cream seal strip, minimal luxury label reading "HUNSET". '
            "Thin climbing ivy strands, one realistic honeybee hovering near the glass, another on a wheat stem behind. "
            "Quiet countryside field during late afternoon, warm sunlight filtering through wheat stalks. "
            "Glowing translucency inside the honey, soft halo edges around jar. Blurred wheat tips and bokeh in foreground. "
            "90mm macro lens, f/2.2, extreme sharpness on jar textures, shallow DOF. Aspect ratio 1:1. "
            "The overall style is a cinematic luxury advertising product shot. No extra text, no watermark."
        ),
    },
    "F02": {
        "name": "Sticker Set Design",
        "category": "F",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Create a premium Pixar-style 3D character sticker set recognizable as the same person from the uploaded photo. "
            "3x3 grid layout (9 stickers total). Aspect ratio 4:5, 8K resolution. Clean cream background. "
            "Preserve exact facial structure, hairstyle, grooming details, unique features. Do NOT over-beautify. "
            "Pixar-style 3D — glossy rendering, soft global illumination, smooth shading, high-detail facial textures. "
            "All stickers head-and-shoulders only. Each sticker has a different outfit (no repetition). "
            "9 expressions: 1.Happy smile 2.Laughing 3.Cool(sunglasses) 4.Angry/serious 5.Surprised "
            "6.Thinking 7.Wink 8.Love(heart gesture) 9.Thumbs up. "
            "Bold clean outline, slightly exaggerated proportions, smooth rounded bottom cutout per sticker. "
            "The overall style is a premium collectible sticker pack with consistent identity. No text labels."
        ),
    },
    "F03": {
        "name": "Interior Design",
        "category": "F",
        "needs_photo": True,
        "photo_type": "room",
        "prompt": (
            "Redesign the room in the uploaded photo in modern Scandinavian minimalist style. "
            "Preserve exact room layout, dimensions, and architectural features (windows, doors, ceiling). "
            "Furniture: clean-lined oak furniture — low-profile platform sofa in natural linen, "
            "minimalist round coffee table, slim bookshelf with curated objects. "
            "Colors: warm whites and light grays for walls, natural wood tones, soft sage green and dusty rose accents. "
            "Flooring: light oak herringbone with large hand-woven wool area rug in cream. "
            "Textiles: linen curtains in off-white, chunky knit throw, muted-tone cushions. "
            "Lighting: sculptural pendant light, warm 2700K ambient, natural daylight enhanced. "
            "Plants: fiddle leaf fig, trailing pothos, ceramic vases, curated books. "
            "Photorealistic architectural visualization. Wide-angle interior photography. Aspect ratio 16:9. "
            "The overall style is a magazine-quality interior design visualization. No text, no watermark."
        ),
    },
    "F04": {
        "name": "Logo Design",
        "category": "F",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            'Design a professional combination mark logo for a brand named "ALPINE". '
            "Icon: minimalist geometric mountain peak with rising sun — triangle for mountain, circle for sun, "
            "negative space creating horizon line. "
            '"ALPINE" in clean modern sans-serif typeface — medium weight, generous letter-spacing, all caps. '
            "Colors: primary deep navy blue (#1B365D), accent warm gold (#D4A855). Icon uses both colors, wordmark in primary. "
            "Style: modern, clean, timeless — works at 16px favicon size and on a billboard. "
            "No gradients, no shadows, no 3D effects — flat, vector-clean design. "
            "Icon centered above wordmark, balanced vertical stacking. Generous padding. White background. "
            "Centered square format. Aspect ratio 1:1. "
            "The overall style is a premium professionally designed brand logo communicating trust and innovation."
        ),
    },
    "F05": {
        "name": "Merchandise / Keychain Design",
        "category": "F",
        "needs_photo": True,
        "photo_type": "selfie",
        "prompt": (
            "Design a premium chibi-style collectible figure based on the uploaded photo. "
            "Slightly oversized head, expressive face preserving key features, dynamic action pose. "
            "High-quality PVC figure with smooth matte finish, subtle metallic paint accents. "
            "Dynamic stance — one foot forward, arm outstretched, slight twist at waist. "
            "Stylized version of the subject's clothing with added fantasy elements. "
            "Sleek circular black acrylic display base. "
            "Product photography style — centered on gradient gray backdrop, soft even illumination, rim light for edges. "
            "Slightly low angle looking up for heroic perspective. Aspect ratio 1:1. "
            "The overall style is a premium collectible figure product photo ready for pre-order announcement. No text, no watermark."
        ),
    },
    "F06": {
        "name": "Coloring Book Page",
        "category": "F",
        "needs_photo": False,
        "photo_type": None,
        "prompt": (
            "Create a detailed coloring book page featuring an enchanted garden scene with a fairy sitting on a mushroom, "
            "surrounded by flowers, butterflies, and a small cottage in the background. "
            "Professional coloring book illustration — clean crisp black line art on pure white background. "
            "Lines varying between 1-3pt weight — thicker outlines for main subjects, thinner for details. "
            "Rich fillable areas of varying sizes — large simple areas and intricate pattern-filled sections "
            "(mandala patterns, zentangle-inspired fills, decorative borders). "
            "Flowers with detailed petal structures, leaves with vein patterns, decorative swirls and dots. "
            "Main subject centered and prominent, supporting elements framing without overcrowding. "
            "Pure black lines on pure white — NO gray, NO gradients, NO fills. All areas fully enclosed. "
            "Aspect ratio 3:4 portrait. "
            "The overall style is a premium coloring book page with intricate detail and satisfying patterns. No pre-filled colors."
        ),
    },
}

PHOTO_TYPE_MAP = {
    "selfie": "selfie.jpg",
    "pet": "pet.jpg",
    "baby": "baby.jpg",
    "room": "room.jpg",
}


def get_reference_image(photo_type: str) -> str | None:
    if not photo_type:
        return None
    filename = PHOTO_TYPE_MAP.get(photo_type)
    if not filename:
        return None
    path = SAMPLES_DIR / filename
    if path.exists():
        return str(path)
    print(f"  WARNING: Sample image not found: {path}")
    return None


async def run_template(template_id: str, runs: int = 2) -> list[dict]:
    tmpl = TEMPLATES[template_id]
    ref_image = get_reference_image(tmpl.get("photo_type")) if tmpl["needs_photo"] else None

    if tmpl["needs_photo"] and not ref_image:
        print(f"\n[{template_id}] SKIP — requires {tmpl['photo_type']} photo but sample not found")
        return []

    results = []
    for run_idx in range(1, runs + 1):
        output_dir = RESULTS_DIR / template_id
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir / f"run_{run_idx}.png")

        print(f"\n{'='*60}")
        print(f"[{template_id}] {tmpl['name']} — Run {run_idx}/{runs}")
        print(f"Prompt: {tmpl['prompt'][:100]}...")
        if ref_image:
            print(f"Reference: {ref_image}")

        result = await generate_image(
            prompt=tmpl["prompt"],
            output_path=output_path,
            reference_image=ref_image,
        )

        meta = {
            "template_id": template_id,
            "template_name": tmpl["name"],
            "category": tmpl["category"],
            "run_index": run_idx,
            "prompt": tmpl["prompt"],
            "reference_image": ref_image,
            "output": output_path if result["success"] else None,
            "success": result["success"],
            "error": result.get("error"),
            "text_response": result.get("text"),
            "timestamp": datetime.now().isoformat(),
        }
        results.append(meta)

        status = "OK" if result["success"] else f"FAILED: {result.get('error')}"
        print(f"Result: {status}")

    return results


async def run_all(category: str = None, template_id: str = None, runs: int = 2):
    get_client()
    print(f"Model: {get_model_name()}")
    print(f"Runs per template: {runs}")

    all_results = {}
    templates_to_run = {}

    if template_id:
        if template_id in TEMPLATES:
            templates_to_run[template_id] = TEMPLATES[template_id]
        else:
            print(f"ERROR: Unknown template ID: {template_id}")
            return
    elif category:
        templates_to_run = {k: v for k, v in TEMPLATES.items() if v["category"] == category}
        if not templates_to_run:
            print(f"ERROR: No templates found for category: {category}")
            return
    else:
        templates_to_run = TEMPLATES

    print(f"Templates to evaluate: {len(templates_to_run)}")

    for tid in templates_to_run:
        results = await run_template(tid, runs=runs)
        if results:
            all_results[tid] = results

    meta_path = RESULTS_DIR / "evaluation-meta.json"
    existing = {}
    if meta_path.exists():
        try:
            with open(meta_path) as f:
                existing = json.load(f)
        except Exception:
            pass
    existing.update(all_results)
    with open(meta_path, "w") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print(f"\nAll metadata saved to {meta_path}")

    success_count = sum(1 for runs in all_results.values() for r in runs if r["success"])
    total_count = sum(len(runs) for runs in all_results.values())
    print(f"\nSummary: {success_count}/{total_count} generations successful")


def interactive_scoring():
    """Interactive mode for scoring generated images."""
    meta_path = RESULTS_DIR / "evaluation-meta.json"
    if not meta_path.exists():
        print("No evaluation metadata found. Run evaluation first.")
        return

    with open(meta_path) as f:
        all_results = json.load(f)

    scores = {}
    dimensions = ["prompt_adherence", "identity_preservation", "visual_quality", "style_accuracy", "overall"]

    for tid, runs in all_results.items():
        successful_runs = [r for r in runs if r["success"]]
        if not successful_runs:
            continue

        print(f"\n{'='*60}")
        print(f"Template: [{tid}] {runs[0]['template_name']}")
        print(f"Successful runs: {len(successful_runs)}")
        for r in successful_runs:
            print(f"  Run {r['run_index']}: {r['output']}")

        template_scores = {}
        for dim in dimensions:
            while True:
                try:
                    score = float(input(f"  {dim} (1-5, or 's' to skip): "))
                    if 1 <= score <= 5:
                        template_scores[dim] = score
                        break
                    print("  Score must be between 1 and 5")
                except ValueError:
                    print(f"  Skipping {tid}")
                    break

        if template_scores:
            scores[tid] = {
                "template_name": runs[0]["template_name"],
                "category": runs[0]["category"],
                "scores": template_scores,
                "notes": input("  Notes (optional): ") or "",
                "timestamp": datetime.now().isoformat(),
            }

    scores_path = RESULTS_DIR / "scores.json"
    with open(scores_path, "w") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)
    print(f"\nScores saved to {scores_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Template Evaluation Runner")
    parser.add_argument("--category", choices=["L", "M", "P"],
                        help="Run only templates in this category")
    parser.add_argument("--template", help="Run a single template by ID (e.g., A01)")
    parser.add_argument("--runs", type=int, default=2, help="Number of runs per template")
    parser.add_argument("--score", action="store_true", help="Interactive scoring mode")
    args = parser.parse_args()

    if args.score:
        interactive_scoring()
    else:
        asyncio.run(run_all(category=args.category, template_id=args.template, runs=args.runs))
