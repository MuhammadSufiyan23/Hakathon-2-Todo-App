# Beautiful Todo Frontend Quickstart Guide

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn package manager
- Git for version control

### Installation Steps

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Initialize shadcn/ui components**
```bash
npx shadcn-ui@latest init
```

4. **Install additional dependencies**
```bash
npm install framer-motion next-themes sonner lucide-react @tanstack/react-query @better-auth/react better-auth
```

5. **Start the development server**
```bash
npm run dev
# or
yarn dev
```

The application will be available at http://localhost:3000

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8080
BETTER_AUTH_SECRET=your-secret-key-here

# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080/api
```

## Key Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run TypeScript and ESLint checks
- `npm run prettier` - Format code with Prettier

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication routes
│   ├── (dashboard)/       # Protected dashboard routes
│   ├── layout.tsx         # Root layout
│   └── providers.tsx      # Global providers
├── components/            # Reusable React components
│   ├── ui/               # shadcn/ui components
│   ├── auth/             # Authentication components
│   ├── dashboard/        # Dashboard layout components
│   └── tasks/            # Task management components
├── lib/                  # Utility functions and API client
├── hooks/                # Custom React hooks
├── styles/               # Global styles
└── public/               # Static assets
```

## Development Workflow

### Creating New Components
1. Place new components in the appropriate subdirectory in `components/`
2. Use PascalCase for component names
3. Export components individually in index.ts files
4. Follow the existing component patterns for consistency

### Adding New Pages
1. Create new directories in `app/` following the App Router convention
2. Use page.tsx for route pages
3. Apply the appropriate layout wrappers
4. Implement proper loading and error states

### Working with Animations
1. Define reusable motion variants in `lib/animations.ts`
2. Use Framer Motion's `motion` components for animated elements
3. Respect user's reduced motion preferences
4. Test animations on various devices

### API Integration
1. Use the centralized API client in `lib/api.ts`
2. Leverage React Query for data fetching and caching
3. Implement proper error handling and loading states
4. Use optimistic updates where appropriate

## Testing Locally

1. **Authentication Flow**: Test sign up, sign in, and logout functionality
2. **Task Operations**: Verify create, read, update, delete operations
3. **Responsive Design**: Test on various screen sizes
4. **Theme Switching**: Verify dark/light mode functionality
5. **Animations**: Ensure smooth performance across devices
6. **Accessibility**: Test keyboard navigation and screen readers

## Troubleshooting

### Common Issues
- **Module not found**: Ensure all dependencies are installed and properly imported
- **TypeScript errors**: Check interface definitions and prop types
- **Animation jank**: Verify transform/opacity properties are used for animations
- **Theme not persisting**: Check next-themes implementation and localStorage access

### Performance Tips
- Use React.memo for expensive components
- Implement proper key props for lists
- Optimize images and static assets
- Monitor bundle size with webpack-bundle-analyzer