import { NextRequest, NextResponse } from 'next/server'
import Anthropic from '@anthropic-ai/sdk'

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

const model = 'claude-sonnet-4-0'

async function searchWikipedia(
  query: string
): Promise<Array<{ title: string; url: string }>> {
  const url = 'https://en.wikipedia.org/w/api.php'
  const params = new URLSearchParams({
    action: 'query',
    list: 'search',
    srsearch: query,
    format: 'json',
    srlimit: '5',
  })

  const response = await fetch(`${url}?${params}`)
  const data = (await response.json()) as {
    query?: { search?: Array<{ title: string; pageid: number }> }
  }
  return (
    data.query?.search?.map((result) => ({
      title: result.title,
      url: `https://en.wikipedia.org/wiki/${encodeURIComponent(result.title)}`,
    })) || []
  )
}

async function getWikipediaContent(title: string): Promise<string> {
  const url = 'https://en.wikipedia.org/w/api.php'
  const params = new URLSearchParams({
    action: 'query',
    titles: title,
    prop: 'extracts',
    exintro: 'true',
    explaintext: 'true',
    format: 'json',
  })

  const response = await fetch(`${url}?${params}`)
  const data = (await response.json()) as {
    query?: { pages?: Record<string, { extract?: string }> }
  }
  const pages = data.query?.pages
  if (!pages) return 'Content not found.'

  for (const page of Object.values(pages)) {
    if (page.extract) {
      return page.extract
    }
  }
  return 'Content not found.'
}

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json()

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    const session = await initMCPSession()

    const result = await session.callTool('research_topic', {
      topic: message,
    })

    let responseText = ''
    if (Array.isArray(result.content)) {
      responseText = result.content
        .filter(
          (item) =>
            typeof item === 'object' &&
            item !== null &&
            'type' in item &&
            item.type === 'text'
        )
        .map((item) => ('text' in item ? item.text : ''))
        .join('\n')
    } else if (
      typeof result.content === 'object' &&
      result.content !== null &&
      'type' in result.content &&
      result.content.type === 'text'
    ) {
      responseText = 'text' in result.content ? String(result.content.text) : ''
    } else {
      responseText = String(result.content)
    }

    // Stream the response character by character
    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        const chunkDelay = 10 // ms between chunks for smooth streaming
        for (let i = 0; i < responseText.length; i++) {
          controller.enqueue(encoder.encode(responseText[i]))
          await new Promise((resolve) => setTimeout(resolve, chunkDelay))
        }
        controller.close()
      },
    })

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Transfer-Encoding': 'chunked',
      },
    })
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    console.error('Error in chat API:', error)
    return NextResponse.json(
      { error: 'Failed to process request', details: errorMessage },
      { status: 500 }
    )
  }
}
