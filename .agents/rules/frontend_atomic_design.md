# FRONTEND ATOMIC DESIGN RULES

All frontend development in this project MUST follow the **Atomic Design** methodology to ensure scalability, maintainability, and consistency.

## 🧱 Component Hierarchy

### 1. Atoms (Basic UI Elements)
Atoms are the basic building blocks that cannot be broken down further.
- **Location**: `src/components/atoms/`
- **Examples**: Buttons, Inputs, Labels, Icons, Badges, Typography.
- **Rule**: Use Ant Design (antd) atoms directly when possible. Create custom atoms only for project-specific base styles.

### 2. Molecules (Simple Components)
Molecules are groups of atoms functioning together as a unit.
- **Location**: `src/components/molecules/`
- **Examples**: SearchBar (Label+Input+Button), NavLink (Icon+Text), FormField.
- **Rule**: Follow the **Single Responsibility Principle**.

### 3. Organisms (Complex Sections)
Organisms are groups of molecules, atoms, and/or other organisms that form a distinct section of the interface.
- **Location**: `src/components/organisms/`
- **Examples**: Navbar, HeroSection, Sidebar, LiveConsole, HistoryTable.
- **Rule**: Organisms should be portable and represent meaningful sections of a page.

### 4. Templates (Layout Skeletons)
Templates define the layout structure and placement of components (skeleton).
- **Location**: `src/components/templates/`
- **Examples**: DashboardLayout, HomepageTemplate.
- **Rule**: Templates should focus on content structure rather than final content.

### 5. Pages (Final UI)
Pages are specific instances of templates with real/mock data applied.
- **Location**: `src/app/` (Next.js App Router)
- **Rule**: Pages should be thin and primarily used for data fetching and assembling templates/organisms.

## 📂 Directory Structure

```text
src/
  ├── components/
  │   ├── atoms/
  │   ├── molecules/
  │   ├── organisms/
  │   └── templates/
  └── app/ (Pages)
```

## 🛠️ Implementation Rules

1.  **Strict Isolation**: A component in a lower level (e.g., Atom) MUST NOT depend on a component in a higher level (e.g., Molecule).
2.  **Ant Design Integration**: Always prefer Ant Design components as the foundation for Atoms and Molecules.
3.  **No Monoliths**: If a file exceeds 150 lines, it should likely be broken down into smaller atomic pieces.
4.  **Styling**: Use Tailwind CSS for ad-hoc styling and antd tokens for theme-consistency. Custom CSS in `globals.css` should be a last resort.
