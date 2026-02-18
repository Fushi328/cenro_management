# ECO-TRACK Design System
## Modern, Clean, Professional Wetland Management Dashboard

---

## 🎨 Design Philosophy

**ECO-TRACK** is a **government-grade environmental management system** designed with:
- **Modern aesthetics** - Clean, minimal, professional
- **Eco-friendly branding** - Green, blue, earth tones
- **Professional UI** - Government system standards
- **Clear information hierarchy** - Easy-to-scan layouts
- **Responsive design** - Works on desktop (desktop-first)
- **Accessibility** - High contrast, readable fonts

---

## 🌈 Color Palette

### Primary Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Primary Green** | `#1e7a4d` | Primary actions, main branding |
| **Secondary Green** | `#2d9e6d` | Hover states, secondary actions |
| **Light Green** | `#a8d5ba` | Light backgrounds, accents |
| **Forest Green** | `#0b4d2c` | Dark accents, borders |

### Water Colors
| Color | Hex | Usage |
|-------|-----|-------|
| **Sky Blue** | `#5b9bd5` | Secondary data, statistics |
| **Ocean Blue** | `#2d6a9f` | Links, hover states |
| **Water Teal** | `#4a9b9e` | Aquatic services, charts |

### Earth Tones
| Color | Hex | Usage |
|-------|-----|-------|
| **Earth Brown** | `#8b6f47` | Borders, text accents |
| **Sand Beige** | `#d4c5a0` | Light backgrounds |

### Status Colors
| Status | Color | Hex | Usage |
|--------|-------|-----|-------|
| **Pending** | Orange | `#f39c12` | Requires action |
| **Approved** | Green | `#27ae60` | Verified/Approved |
| **Completed** | Blue | `#2980b9` | Finished tasks |
| **Rejected** | Red | `#e74c3c` | Error/Rejection |
| **Warning** | Orange | `#e67e22` | Caution states |

### Neutral Palette
| Color | Hex | Usage |
|-------|-----|-------|
| **White** | `#ffffff` | Card backgrounds |
| **Off-White** | `#f8faf9` | Page background |
| **Light Gray** | `#f1f3f2` | Hover states |
| **Medium Gray** | `#d9dcd9` | Borders |
| **Dark Gray** | `#2c3e50` | Text content |
| **Text Gray** | `#5a6c6d` | Secondary text |

---

## 🔤 Typography

### Font Family
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
```

### Font Sizes & Weights

| Element | Size | Weight | Usage |
|---------|------|--------|-------|
| **Page Title** | 28px | 700 (bold) | Dashboard heading |
| **Card Title** | 20px | 600 | Section headings |
| **Subtitle** | 16px | 400 | Description text |
| **Body Text** | 14px | 400 | General content |
| **Small Text** | 12px | 400 | Helper text, badges |
| **Uppercase Label** | 14px | 500 | Form labels, tab titles |

### Line Height
- Body: `1.6`
- Headings: `1.4`
- Letter spacing: `-0.5px` (compact look)

---

## 🎯 Components

### 1. Navigation Bar
**Location:** Fixed at top (70px height)  
**Background:** White with subtle gradient + green bottom border  
**Features:**
- ECO-TRACK logo with emoji icon (🌍)
- Active nav link underline animation
- User section with logout button
- Responsive hamburger (mobile)

```html
<header class="top-nav">
    <div class="nav-container">
        <a href="/" class="logo">
            <span class="logo-icon">🌍</span>
            <div>
                <span class="logo-text">ECO-TRACK</span>
                <span class="logo-subtitle">Wetland Management</span>
            </div>
        </a>
        <nav class="top-nav-links">
            <!-- Navigation items -->
        </nav>
    </div>
</header>
```

**Styles:**
- Logo animation: Float effect (subtle up-down movement)
- Active link: Green color + bottom border glow
- User section: Light green background + red logout button

---

### 2. Admin Header
**Location:** Below main nav for admin users  
**Sections:**
- Page title (32px, bold)
- Quick action buttons (Export, Operations)
- Primary navigation tabs

**Tab Styling:**
- Active tab: Green text + green bottom border + light background
- Hover: Green text + light background
- Icons + text (e.g., "📊 Dashboard")

---

### 3. Cards
**Structure:**
```html
<div class="card">
    <div class="card-header">
        <h3 class="card-title">Card Title</h3>
        <p class="card-subtitle">Supporting text</p>
    </div>
    <div class="card-content">
        <!-- Content here -->
    </div>
</div>
```

**Styles:**
- White background
- 12px border radius
- 25px padding
- Shadow: `0 4px 12px rgba(30, 122, 77, 0.15)`
- Bottom margin: 25px

---

### 4. Summary Cards (Dashboard)
**Grid:** Auto-fit columns (min 250px)  
**Card Elements:**
- Large emoji icon (48px, 0.7 opacity)
- Title (uppercase, small, gray)
- Value (36px, bold, dark)
- Trend/Status (small text)
- Left border: 4px colored stripe

**Card Types:**
```
.summary-card.total       → Sky Blue border
.summary-card.pending     → Orange border
.summary-card.completed   → Green border
.summary-card.active      → Ocean Blue border
```

---

### 5. Data Tables
**Structure:**
```html
<table class="data-table">
    <thead>
        <tr>
            <th>Column Title</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data</td>
        </tr>
    </tbody>
</table>
```

**Styles:**
- Header background: Light gray
- Row hover: Light gray background
- Text: Small (14px), uppercase header labels
- Borders: Bottom border only (lighter gray)

---

### 6. Status Badges
**Available Status Types:**

```html
<span class="status-badge status-pending">Pending</span>
<span class="status-badge status-approved">Approved</span>
<span class="status-badge status-completed">Completed</span>
<span class="status-badge status-scheduled">Scheduled</span>
```

**Styles:**
- Inline-block element
- Padding: 4px 12px
- Border radius: 20px (pill shape)
- Font size: 12px, weight 500

---

### 7. Progress Bars
**Structure:**
```html
<div class="progress-bar-container">
    <div class="progress-bar" style="width: 65%;">65%</div>
</div>
```

**Styles:**
- Container: Light gray background, 10px rounded
- Bar: Green, smooth transition (0.3s)
- Height: 24px
- Text: White, centered, bold

---

### 8. Forms & Inputs
**Text Input:**
```html
<input type="text" class="form-control" placeholder="Enter text">
```

**Styles:**
- Width: 100%
- Padding: 10px 15px
- Border: 1px solid medium-gray
- Border radius: 6px
- Focus: Green border + light green shadow
- Transition: 0.3s

**Form Group:**
```html
<div class="form-group">
    <label>Field Label</label>
    <input type="text" class="form-control">
</div>
```

---

### 9. Buttons
**Button Classes:**

```html
<!-- Primary Button -->
<button class="btn btn-primary">Action</button>

<!-- Success Button -->
<button class="btn btn-success">Confirm</button>

<!-- Warning Button -->
<button class="btn btn-warning">Caution</button>

<!-- Small Button -->
<button class="btn btn-sm btn-primary">Small</button>
```

**Styles:**
- Padding: 10px 20px (normal), 6px 12px (small)
- Border radius: 6px
- Transition: 0.3s (hover effects)
- Font weight: 500

**Color Schemes:**
- Primary: Green bg → darker green hover
- Success: Green
- Warning: Orange
- Info: Blue
- Logout: Red bg → darker red hover

---

### 10. Alerts/Messages
**Alert Types:**

```html
<div class="alert alert-success">Success message</div>
<div class="alert alert-error">Error message</div>
<div class="alert alert-warning">Warning message</div>
```

**Styles:**
- Padding: 12px 20px
- Border radius: 6px
- Border: 1px colored
- Margin bottom: 10px

---

## 📐 Layout Grid

### Main Container
```css
max-width: 1400px;
margin: 0 auto;
padding: 0 30px; /* Horizontal padding */
```

### Spacing Scale
- **XS:** 5px
- **S:** 10px
- **M:** 15px
- **L:** 20px
- **XL:** 25px
- **2XL:** 30px

### Summary Cards Grid
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
gap: 20px;
```

### Charts Grid
```css
display: grid;
grid-template-columns: 2fr 1fr;
gap: 25px;
```

---

## 🎨 Shadows & Effects

### Shadow Hierarchy
```css
--shadow-sm: 0 1px 3px rgba(30, 122, 77, 0.1);
--shadow-md: 0 4px 12px rgba(30, 122, 77, 0.15);
--shadow-lg: 0 8px 24px rgba(30, 122, 77, 0.2);
```

### Animations
- **Button Hover:** `translateY(-2px)` + shadow increase
- **Logo:** `float` animation (3s loop, ±5px)
- **Nav Link:** Underline width expansion (0.3s)
- **All Transitions:** 0.3s ease-in-out

---

## 📊 Chart Styling

### Chart.js Integration
**Colors:**
- Dataset 1: `#2d9e6d` (Secondary Green)
- Dataset 2: `#5b9bd5` (Sky Blue)
- Background: `rgba(45, 158, 109, 0.1)`

**Configuration:**
```javascript
{
  type: 'bar',
  options: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    }
  }
}
```

---

## 🎯 Pages Overview

### 1. Home Page (Consumer)
- Hero section with eco-friendly imagery
- Quick action buttons
- Service types overview
- How it works section
- FAQ/Contact

### 2. Login Page
- Centered card (400px width)
- Form with validation
- "Forgot Password" link
- "Register" link
- Centered logo

### 3. Admin Dashboard
- **4 Summary Cards** (requests, pending, completed, active units)
- **2-Column Chart Section:**
  - Service trends bar chart (left, 2fr)
  - Distribution breakdown (right, 1fr)
- **Barangay Ranking Table** (full width)
- **Quick Actions Grid** (4 buttons)
- **System Status Card**

### 4. Service Requests (Admin)
- **Tab Navigation:**
  - Pending (yellow badge)
  - Approved (blue badge)
  - Schedule (by barangay + 10-person limit)
  - Completed (gray badge)
- Request cards with action buttons
- Search/Filter functionality

### 5. Membership Management (Admin)
- **Tab Navigation:**
  - Registration (new members)
  - Account Management (active members)
  - Service History (4-year cycle tracking)
- Member list with details
- Action buttons (View, Edit, Approve)

### 6. Service Computation (Admin)
- Form inputs on left (50% width)
- Computation results on right (50% width)
- Category selection
- Cubic meters input
- Location toggle (inside/outside Bayawan)
- Charges breakdown display
- Print receipt button

### 7. Declogging Application (Admin)
- Applicant information form
- Signature upload areas
- CENRO representative selection
- Date pickers
- Print application button

---

## 📱 Responsive Breakpoints

### Mobile-First Approach (but Desktop-Optimized)

**Tablet (768px and below):**
- Single-column layout for summary cards
- Stacked chart grid (1fr instead of 2fr 1fr)
- Mobile-friendly navigation
- Hamburger menu

**Mobile (480px and below):**
- Simplified header
- All elements single-column
- Larger touch targets (44px min)
- Collapsible sections

---

## 🔍 Focus States & Accessibility

### Keyboard Navigation
- Tab order: Left to right, top to bottom
- Focus outline: 2px solid green
- Skip-to-content link (hidden but accessible)

### Color Contrast
- Text on white: `#2c3e50` (dark gray) - WCAG AAA
- Status badges: High contrast colors
- Link colors: `#2d6a9f` (ocean blue)

### Icons & Emojis
- All icons have text labels
- Emoji + text combination (not emoji alone)
- Screen reader friendly

---

## 📝 Component Usage Examples

### Summary Card Example
```html
<div class="summary-card pending">
    <div class="summary-card-icon">⏳</div>
    <div class="summary-card-content">
        <div class="summary-card-title">Pending Service</div>
        <div class="summary-card-value">24</div>
        <div class="summary-card-status">Awaiting execution</div>
    </div>
</div>
```

### Data Table Example
```html
<table class="data-table">
    <thead>
        <tr>
            <th>Rank</th>
            <th>Barangay</th>
            <th>Requests</th>
            <th>Percentage</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>#1</td>
            <td><strong>Barangay Name</strong></td>
            <td>24</td>
            <td>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: 65%;">65%</div>
                </div>
            </td>
        </tr>
    </tbody>
</table>
```

### Form Group Example
```html
<div class="form-group">
    <label for="category">Service Category</label>
    <select id="category" class="form-control">
        <option>Select a category...</option>
        <option>Residential</option>
        <option>Commercial</option>
    </select>
</div>
```

### Alert Example
```html
<div class="alert alert-success">
    ✅ Service request approved successfully!
</div>
```

---

## 🎯 Design Best Practices

### 1. **Visual Hierarchy**
- Use font size, weight, and color to guide attention
- Important info at top/left
- Consistent alignment

### 2. **White Space**
- Generous padding (25px, 20px)
- Breathing room between sections
- Don't overcrowd cards

### 3. **Color Usage**
- Green = primary, positive actions
- Blue = secondary, information
- Orange = attention, pending
- Red = destructive, logout

### 4. **Interactive Elements**
- Clear hover states
- Smooth transitions (0.3s)
- Sufficient padding for touch (44px+)

### 5. **Consistency**
- Same button style throughout
- Consistent icon placement
- Standard spacing units

---

## 📋 Future Enhancements

- [ ] Dark mode toggle
- [ ] Map view for GPS locations
- [ ] Real-time notifications
- [ ] Mobile app version
- [ ] Advanced charting options
- [ ] PDF report generation
- [ ] SMS notification integration
- [ ] File upload drag-and-drop

---

**Last Updated:** January 29, 2026  
**Design System Version:** 1.0  
**Status:** ✅ Active & Maintained
