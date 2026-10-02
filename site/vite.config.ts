import { readdirSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'

const AUTHORS = resolve(__dirname, '../authors')

// Builds a light index (no full text) so the home page doesn't ship 3.6 MB of markdown.
function authorIndex(): Plugin {
  const id = 'virtual:author-index'
  return {
    name: 'author-index',
    resolveId: (source) => (source === id ? '\0' + id : undefined),
    load(source) {
      if (source !== '\0' + id) return
      const index = readdirSync(AUTHORS)
        .filter((f) => f.endsWith('.md'))
        .map((file) => {
          this.addWatchFile(resolve(AUTHORS, file))
          const text = readFileSync(resolve(AUTHORS, file), 'utf8')
          const field = (key: string) => text.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1].trim() ?? ''
          const unlink = (s: string) => s.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
          const summary = text.match(/^## תקציר\s*\n+([^\n]+)/m)?.[1] ?? ''
          return {
            id: Number(field('id')),
            name: unlink(text.match(/^# (.+)$/m)?.[1].trim() ?? field('name').replace(/"/g, '')),
            books: Number(field('db_books')),
            confidence: field('confidence'),
            summary: unlink(summary),
          }
        })
        .sort((a, b) => a.name.localeCompare(b.name, 'he'))
      return `export default ${JSON.stringify(index)}`
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [react(), authorIndex()],
  server: { fs: { allow: ['..'] } },
  build: { chunkSizeWarningLimit: 1000 }, // ponytail: index carries all summaries (~175 kB gz); split if it grows
})
