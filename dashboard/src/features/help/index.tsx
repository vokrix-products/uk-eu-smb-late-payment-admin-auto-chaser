import { useEffect, useState } from 'react'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ChevronDown, ChevronRight, BookOpen, HelpCircle } from 'lucide-react'

interface Section {
  title: string
  content: string
  faqs: { q: string; a: string }[]
}

function parseManual(text: string): Section[] {
  const lines = text.split('\n')
  const sections: Section[] = []
  let current: Section | null = null

  for (const line of lines) {
    const sectionMatch = line.match(/^(\d+)\.\s+(.+)/)
    if (sectionMatch) {
      if (current) sections.push(current)
      current = { title: sectionMatch[2].trim(), content: '', faqs: [] }
      continue
    }
    if (!current) continue
    const qMatch = line.match(/^Q:\s*(.+)/)
    if (qMatch) {
      current.faqs.push({ q: qMatch[1].trim(), a: '' })
      continue
    }
    if (current.faqs.length > 0 && line.startsWith('A:')) {
      current.faqs[current.faqs.length - 1].a = line.replace(/^A:\s*/, '').trim()
      continue
    }
    if (current.faqs.length > 0 && current.faqs[current.faqs.length - 1].a !== '') {
      current.faqs[current.faqs.length - 1].a += ' ' + line.trim()
    } else if (current.faqs.length === 0) {
      current.content += (current.content ? '\n' : '') + line
    }
  }
  if (current) sections.push(current)
  return sections.filter(s => s.title)
}

function FaqItem({ q, a }: { q: string; a: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className='border-b border-border last:border-0'>
      <button
        onClick={() => setOpen(!open)}
        className='flex w-full items-center justify-between py-3 text-left text-sm font-medium hover:text-primary transition-colors'
      >
        <span>{q}</span>
        {open ? <ChevronDown className='h-4 w-4 shrink-0' /> : <ChevronRight className='h-4 w-4 shrink-0' />}
      </button>
      {open && <p className='pb-3 text-sm text-muted-foreground leading-relaxed'>{a}</p>}
    </div>
  )
}

export function Help() {
  const [sections, setSections] = useState<Section[]>([])
  const [active, setActive] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('/api/manual')
      .then(r => r.json())
      .then(d => {
        if (d.manual) setSections(parseManual(d.manual))
        else setError(true)
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  const section = sections[active]

  return (
    <>
      <Header>
        <Search />
        <ThemeSwitch />
        <ProfileDropdown />
      </Header>
      <Main>
        <div className='mb-4 flex items-center gap-2'>
          <BookOpen className='h-5 w-5' />
          <h1 className='text-2xl font-bold tracking-tight'>Help & Documentation</h1>
        </div>
        {loading && (
          <div className='space-y-3'>
            <Skeleton className='h-6 w-48' />
            <Skeleton className='h-4 w-full' />
            <Skeleton className='h-4 w-3/4' />
          </div>
        )}
        {error && (
          <Card>
            <CardContent className='pt-6 text-sm text-muted-foreground'>
              Documentation not available yet for this product.
            </CardContent>
          </Card>
        )}
        {!loading && !error && sections.length > 0 && (
          <div className='flex gap-6'>
            {/* Left nav */}
            <div className='w-56 shrink-0'>
              <Card className='sticky top-4'>
                <CardContent className='p-3'>
                  <nav className='space-y-1'>
                    {sections.map((s, i) => (
                      <button
                        key={i}
                        onClick={() => setActive(i)}
                        className={`w-full rounded-md px-3 py-2 text-left text-sm transition-colors ${
                          active === i
                            ? 'bg-primary/10 text-primary font-medium'
                            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                        }`}
                      >
                        {s.title}
                      </button>
                    ))}
                  </nav>
                </CardContent>
              </Card>
            </div>
            {/* Content */}
            <div className='flex-1 min-w-0'>
              <Card>
                <CardHeader>
                  <CardTitle className='flex items-center gap-2'>
                    <BookOpen className='h-4 w-4' />
                    {section.title}
                  </CardTitle>
                </CardHeader>
                <CardContent className='space-y-4'>
                  {section.content && (
                    <div className='text-sm text-muted-foreground leading-relaxed whitespace-pre-line'>
                      {section.content.trim()}
                    </div>
                  )}
                  {section.faqs.length > 0 && (
                    <div className='mt-4'>
                      <div className='flex items-center gap-2 mb-3'>
                        <HelpCircle className='h-4 w-4 text-primary' />
                        <span className='text-sm font-medium'>Common Questions</span>
                      </div>
                      <div className='rounded-lg border border-border px-4'>
                        {section.faqs.map((faq, i) => (
                          <FaqItem key={i} q={faq.q} a={faq.a} />
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </Main>
    </>
  )
}
