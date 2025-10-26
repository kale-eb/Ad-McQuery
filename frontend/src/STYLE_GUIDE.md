# 🎨 Ad McQuery Style Guide - Cute Capybara UI

## Design Philosophy: "Cute Minimalism"
Transform from technical dashboard to delightfully professional analysis tool. Think **Notion meets Figma meets a cozy coffee shop** - clean, soft, inviting, but still professional for serious ad analysis work.

## 🌈 Color Palette

### Primary Colors
- **Beanie Cream**: `#F8F5F2` - Text boxes, input fields, "paper" elements
- **Soft Tan**: `#E5C9A9` - Primary light background
- **Capybara Brown**: `#C69C6D` - Drop shadows, subtle borders
- **Rosy Cheek**: `#F4C7C7` - Main accent (buttons, links, highlights)
- **Paper Blue**: `#B0C4DE` - Secondary accent (info boxes, highlights)
- **Dark Roast**: `#5D4037` - Main text, borders, outlines

### Functional Colors
- **Success Green**: `#7FB069` - Completed analysis, emotional indices >0.5
- **Warning Amber**: `#F2CC8F` - Processing states, pending analysis
- **Error Coral**: `#E07A5F` - Error messages, failed uploads
- **Data Purple**: `#9B7EBD` - Charts, graphs, data highlights
- **Modal Overlay**: `rgba(93, 64, 55, 0.6)` - Background overlays

## 📝 Typography

### Font Stack
- **Primary**: `'Inter', 'SF Pro Display', system-ui, sans-serif`
- **Accent/Headings**: `'Nunito', 'Poppins', sans-serif` 
- **Monospace**: `'JetBrains Mono', 'Fira Code', monospace`

### Font Weights
- **Regular**: 400
- **Medium**: 500  
- **Semi-bold**: 600
- **No harsh bold weights**

### Typography Scale
- **H1**: 2.5rem (40px) - Page titles
- **H2**: 2rem (32px) - Section headers
- **H3**: 1.5rem (24px) - Component titles
- **H4**: 1.25rem (20px) - Subsection headers
- **Body**: 1rem (16px) - Primary text
- **Small**: 0.875rem (14px) - Secondary text
- **Tiny**: 0.75rem (12px) - Captions, metadata

## 🏗️ Layout & Spacing

### Spacing Scale (8px base unit)
- **xs**: 8px
- **sm**: 16px
- **md**: 24px
- **lg**: 32px
- **xl**: 48px
- **2xl**: 64px

### Layout Rules
- **Page margins**: 32px minimum on desktop
- **Card padding**: 24px internal
- **Component gaps**: 16px between elements
- **Generous breathing room** throughout

## 🎪 Shape Language

### Border Radius Scale
- **xs**: 4px - Small elements
- **sm**: 8px - Input fields
- **md**: 12px - Buttons
- **lg**: 16px - Cards
- **xl**: 24px - Modals
- **pill**: 9999px - Tags, badges

### Component Shapes
- **Cards**: 16px radius with subtle shadows
- **Buttons**: 12px radius, soft corners
- **Input fields**: 8px radius with soft insets
- **Modals**: 24px radius for floating feel
- **Tags/Badges**: Pill shapes

## 🌟 Shadows & Elevation

### Shadow Scale
- **Subtle**: `0 2px 8px rgba(93, 64, 55, 0.08)`
- **Medium**: `0 4px 16px rgba(93, 64, 55, 0.12)`
- **High**: `0 8px 32px rgba(93, 64, 55, 0.16)`
- **Inner**: `inset 0 1px 3px rgba(93, 64, 55, 0.1)`

### Usage
- **Cards**: Subtle elevation by default
- **Hover states**: Medium elevation
- **Modals**: High elevation
- **Input fields**: Inner shadows when focused

## 🎭 Interactive States

### Hover Effects
- Gentle lift with increased shadow
- Soft scale transform (1.02x)
- Color transitions (300ms ease)

### Focus States
- Rosy cheek outline glow
- No harsh focus rings
- Smooth transitions

### Active States
- Slight inset shadow
- Gentle scale down (0.98x)

### Loading States
- Soft pulsing animations
- Skeleton loaders with capybara theme

## 🎨 Component Specifications

### Sidebar
- **Background**: Soft tan
- **Cards**: Rounded with hover animations
- **Dividers**: Gentle, low contrast
- **Capybara integration**: Cute mascot moments

### Upload Zone
- **Style**: Soft, pillowy appearance
- **Border**: Dashed, rosy cheek on drag-over
- **Animation**: Gentle bounce on interactions
- **Progress**: Cute loading animations

### Media Grid
- **Cards**: Rounded previews with soft shadows
- **Hover**: Gentle lift + shadow increase
- **Status badges**: Pill shapes with appropriate colors
- **Spacing**: Generous gaps between items

### Analysis Modal
- **Style**: Floating card with high elevation
- **Sections**: Soft dividers between content
- **Data display**: Clean typography hierarchy
- **Color swatches**: Soft circles instead of squares
- **Close button**: Gentle, accessible

### Buttons
- **Primary**: Rosy cheek background
- **Secondary**: Paper blue background
- **Hover**: Subtle color shift + lift
- **Disabled**: Reduced opacity, no hover effects

### Form Elements
- **Background**: Beanie cream
- **Border**: Capybara brown, rosy cheek on focus
- **Padding**: Generous internal spacing
- **Typography**: Clean, readable font stack

## 🚀 Implementation Notes

### Animation Guidelines
- **Duration**: 200-300ms for micro-interactions
- **Easing**: `ease-out` for natural feel
- **Transforms**: Prefer scale/translate over opacity changes
- **Stagger**: Slight delays for list animations

### Accessibility
- **Contrast**: Maintain WCAG AA standards
- **Focus**: Clear, visible focus indicators
- **Touch targets**: Minimum 44px for interactive elements
- **Animations**: Respect prefers-reduced-motion

### Responsive Behavior
- **Breakpoints**: 768px, 1024px, 1280px
- **Spacing**: Proportional reduction on mobile
- **Typography**: Slightly smaller scales on small screens
- **Touch-friendly**: Larger tap targets on mobile

---

*This guide ensures Ad McQuery maintains its cute, approachable aesthetic while remaining professional and functional for serious ad analysis work.* 🐹✨