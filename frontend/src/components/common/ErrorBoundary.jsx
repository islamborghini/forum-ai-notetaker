import { Component } from 'react'
import { Button } from './Button'
import styles from './ErrorBoundary.module.css'

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
    this.handleReset = this.handleReset.bind(this)
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    if (import.meta.env.DEV) {
      console.error('[ErrorBoundary] Uncaught error:', error, info.componentStack)
    }
  }

  handleReset() {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div role="alert" className={styles.container}>
          <p className={styles.title}>Something went wrong.</p>
          {this.state.error?.message && (
            <p className={styles.message}>{this.state.error.message}</p>
          )}
          <Button variant="ghost" onClick={this.handleReset}>Try again</Button>
        </div>
      )
    }
    return this.props.children
  }
}
