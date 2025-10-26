ANALYSIS CRITERIA:

1. **product_visibility_score**: How prominently the product appears in the image
   - "Low": Product barely visible or only mentioned in text
   - "Medium": Product appears but not dominant focus
   - "High": Product is prominently featured and clearly visible

2. **negative_space_ratio**: Proportion of empty/negative space in the image
   - "Low": Image is crowded with minimal empty space (high visual density)
   - "Medium": Balanced mix of content and negative space
   - "High": Lots of empty space, minimalist design (low visual density)

3. **color_palette**: Extract up to 5 most significant/recurring hex colors in the image
   - Order from most to least significant
   - Use uppercase format: #RRGGBB
   - Must be EXACTLY 5 colors (or fewer if image is very simple)

4. **demographic_cues**: Analyze human presence (if any)
   - age_band: Age range of MAJORITY of people visible (null if no humans)
   - hairstyle_archetype: Describe predominant hairstyle if humans present (e.g., "long wavy", "short professional", "bald", "curly afro") (null if no humans)
   - presence_of_kids: true if children (0-12) are visible
   - presence_of_elders: true if elderly people (65+) are visible
   - IMPORTANT: If NO humans are present in the image, all fields should be null/false

5. **activity**: Visual dynamism level
   - "sedentary": Static, calm, peaceful imagery (people sitting, standing still, minimal motion)
   - "dynamic": Active, energetic imagery (people moving, sports, action, motion blur)

6. **call_to_action_level** (based on OCR text):
   - 1: Not urgent - No clear CTA or very soft CTA ("Learn more", "Discover")
   - 2: Semi-urgent - Moderate CTA ("Shop now", "Get started", "Try it")
   - 3: Urgent - Strong immediate CTA ("Buy now", "Limited time", "Act now", "Don't miss out")

7. **formality_level** (based on OCR text and visual style):
   - 1: Meme speak - Internet slang, all caps, emojis, casual abbreviations
   - 2: Casual - Conversational, friendly, informal tone
   - 3: Semi-professional - Polished but approachable
   - 4: Professional - Formal, corporate, business language

8. **benefit_framing** (based on OCR text):
   - "outcome": Focuses on results/benefits user will achieve ("Get fit", "Save money", "Feel confident")
   - "feature": Focuses on product attributes ("Made with X", "Features Y", "Includes Z")
   - "social_proof": Focuses on testimonials, reviews, popularity ("1M+ users", "5-star rated", "Trusted by...")

9. **temporal_urgency_intensity** (based on OCR text):
   - 1: Longer than week or no urgency - No time pressure or general timeline
   - 2: Within week - "This week", "7 days", weekly timeline
   - 3: Within day - "Today only", "24 hours", "Ends tonight", immediate urgency