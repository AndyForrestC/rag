import { render, screen } from '@testing-library/react'
import { act } from 'react'
import Home from '../app/page'

jest.mock('../app/components/header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header Component</div>
  }
})

jest.mock('../app/components/chat-section', () => {
  return function MockChatSection() {
    return <div data-testid="chat-section">Chat Section Component</div>
  }
})

describe('Home', () => {
  it('renders the main page components', () => {
    act(() => {
      render(<Home />)
    })

    expect(screen.getByTestId('header')).toBeInTheDocument()
    expect(screen.getByTestId('chat-section')).toBeInTheDocument()
  })
})
