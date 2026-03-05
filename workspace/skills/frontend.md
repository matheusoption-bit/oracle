# SKILL: Frontend Development

## Stack
- Next.js 14 App Router
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui

## Convenções

### Estrutura de Componentes
```
src/components/
  [feature]/
    [ComponentName].tsx
    [ComponentName].test.tsx
  ui/  (shadcn)
```

### Naming
- Componentes: PascalCase
- Arquivos: kebab-case
- Props interfaces: `[Component]Props`

### Imports
Sempre absolutos com alias `@/`:
```typescript
import { Button } from '@/components/ui/button';
```

### Estado
- useState para local
- Zustand para global
- Server Components por padrão

### Estilo
- Tailwind classes primeiro
- CSS modules se necessário
- Nunca inline styles

## Scaffold Padrão

Para nova tela:
1. `npx create-next-app@latest`
2. `npx shadcn-ui@latest init`
3. Adicionar componentes: `npx shadcn-ui@latest add [nome]`

## Validação

Antes de considerar concluído:
- [ ] `npm run build` sem erros
- [ ] `npm run lint` sem warnings
- [ ] TypeScript strict ok
- [ ] Screenshot tirado via Browser sub-agent
