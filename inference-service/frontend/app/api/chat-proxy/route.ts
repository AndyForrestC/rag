import { NextRequest } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    console.log('Received from frontend:', body);
    
    // Transform useChat format to backend format
    const backendPayload = {
      messages: body.messages || [],
      session_id: body.session_id || null
    };

    console.log('Sending to backend:', backendPayload);

    // Forward to backend with a timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

    try {
      const backendResponse = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendPayload),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!backendResponse.ok) {
        console.error('Backend error:', backendResponse.status, backendResponse.statusText);
        const errorText = await backendResponse.text();
        console.error('Error details:', errorText);
        return new Response(`Backend error: ${backendResponse.statusText}`, {
          status: backendResponse.status,
        });
      }

      // For streaming responses, just pipe through
      return new Response(backendResponse.body, {
        headers: {
          'Content-Type': 'text/plain; charset=utf-8',
          'Cache-Control': 'no-cache',
        },
      });
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error('Request timeout');
        return new Response('Request timeout', { status: 408 });
      }
      throw fetchError;
    }
  } catch (error) {
    console.error('Proxy error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(`Internal Server Error: ${errorMessage}`, { status: 500 });
  }
}
