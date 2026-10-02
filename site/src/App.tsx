import { useDeferredValue, useEffect, useMemo, useState, useSyncExternalStore } from 'react'
import Markdown, { type Components } from 'react-markdown'
import index from 'virtual:author-index'
import licenses from '../../LICENSES.md?raw'

type Author = (typeof index)[number]

const files = import.meta.glob<string>('../../authors/*.md', { query: '?raw', import: 'default' })
const byId = new Map(index.map((a) => [a.id, a]))

const CONFIDENCE: Record<string, string> = {
  high: 'ודאות גבוהה',
  medium: 'ודאות בינונית',
  low: 'ודאות נמוכה',
}

// Hash routing: GitHub Pages has no rewrites, so #/author/12 survives a reload.
const subscribe = (cb: () => void) => {
  addEventListener('hashchange', cb)
  return () => removeEventListener('hashchange', cb)
}
const useHash = () => useSyncExternalStore(subscribe, () => location.hash.slice(1) || '/')

// Drops niqqud, geresh and quote marks so «רמב"ם» matches «רמב״ם».
const normalize = (s: string) => s.replace(/[֑-ׇ"'״׳־\-]/g, '').toLowerCase()

export default function App() {
  const path = useHash()
  const [route, param = ''] = path.slice(1).split(/\/(.*)/)

  useEffect(() => scrollTo(0, 0), [route, param])

  return (
    <>
      <header className="masthead">
        <a href="#/" className="brand">
          ביוגרפיות המחברים
        </a>
        <nav>
          <a href="#/about">רישיון</a>
        </nav>
      </header>
      <main>
        {route === 'author' ? (
          <AuthorPage id={Number(param)} />
        ) : route === 'about' ? (
          <article className="prose">
            <Markdown>{licenses}</Markdown>
          </article>
        ) : (
          <Home initialQuery={route === 'search' ? decodeURIComponent(param) : ''} />
        )}
      </main>
      <footer className="colophon">
        {index.length} מחברים · הטקסט מופץ ברישיון{' '}
        <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.he">CC BY-SA 4.0</a>
      </footer>
    </>
  )
}

function Home({ initialQuery }: { initialQuery: string }) {
  const [query, setQuery] = useState(initialQuery)
  const deferred = useDeferredValue(query)
  useEffect(() => setQuery(initialQuery), [initialQuery])

  const groups = useMemo(() => {
    const q = normalize(deferred.trim())
    const hits = q ? index.filter((a) => normalize(a.name + ' ' + a.summary).includes(q)) : index
    const map = new Map<string, Author[]>()
    for (const a of hits) {
      const letter = a.name[0]
      map.set(letter, [...(map.get(letter) ?? []), a])
    }
    return [...map]
  }, [deferred])

  const count = groups.reduce((n, [, list]) => n + list.length, 0)

  return (
    <>
      <section className="intro">
        <h1>מחברי הספרים שבמאגר</h1>
        <p>
          לכל מחבר: תקציר, תולדות חייו, חיבוריו ומקורות. {index.length} ערכים, מסודרים לפי
          האלף־בית.
        </p>
        <input
          type="search"
          className="search"
          placeholder="חיפוש לפי שם, מקום או ספר"
          aria-label="חיפוש"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
        <nav className="letters" aria-label="קפיצה לאות">
          {groups.map(([letter]) => (
            <a key={letter} href={`#letter-${letter}`} onClick={jumpTo(letter)}>
              {letter}
            </a>
          ))}
        </nav>
      </section>

      {count === 0 && <p className="empty">לא נמצא מחבר בשם הזה.</p>}

      {groups.map(([letter, list]) => (
        <section key={letter} className="group" id={`letter-${letter}`}>
          <h2 className="letter">{letter}</h2>
          <ul className="entries">
            {list.map((a) => (
              <li key={a.id}>
                <a href={`#/author/${a.id}`} className="entry">
                  <span className="entry-name">{a.name}</span>
                  <span className="entry-summary">{a.summary}</span>
                  <span className="entry-meta">{books(a.books)}</span>
                </a>
              </li>
            ))}
          </ul>
        </section>
      ))}
    </>
  )
}

// Letter anchors would clobber the hash route, so scroll manually.
const jumpTo = (letter: string) => (e: React.MouseEvent) => {
  e.preventDefault()
  document.getElementById(`letter-${letter}`)?.scrollIntoView({ behavior: 'smooth' })
}

const books = (n: number) => (n === 1 ? 'ספר אחד במאגר' : `${n} ספרים במאגר`)

function AuthorPage({ id }: { id: number }) {
  const author = byId.get(id)
  const [text, setText] = useState<string>()

  useEffect(() => {
    setText(undefined)
    const load = files[`../../authors/${String(id).padStart(4, '0')}.md`]
    load?.().then((raw) =>
      // Front matter and the H1 are rendered by the header below.
      setText(raw.replace(/^---[\s\S]*?---\s*/, '').replace(/^# .+\n/, '')),
    )
  }, [id])

  if (!author) return <p className="empty">המחבר לא נמצא.</p>

  return (
    <article className="prose">
      <a href="#/" className="back">
        → כל המחברים
      </a>
      <h1>{author.name}</h1>
      <p className="byline">
        {books(author.books)}
        {CONFIDENCE[author.confidence] && <> · {CONFIDENCE[author.confidence]}</>}
      </p>
      {text === undefined ? <p className="loading">טוען…</p> : <Markdown components={components}>{text}</Markdown>}
    </article>
  )
}

const components: Components = {
  a({ href = '', children }) {
    // zayit:// links open the desktop app; on the web, books become plain text and searches stay in-site.
    if (href.startsWith('zayit://search/')) return <a href={`#/search/${href.slice(15)}`}>{children}</a>
    if (href.startsWith('zayit://')) return <span className="book">{children}</span>
    return (
      <a href={href} target="_blank" rel="noreferrer">
        {children}
      </a>
    )
  },
}
