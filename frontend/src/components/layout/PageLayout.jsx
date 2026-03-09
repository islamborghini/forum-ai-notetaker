import { Navbar } from './Navbar'
import { GridBackground } from './backgrounds/GridBackground'
import styles from './PageLayout.module.css'

/**
 * @param {{ children: React.ReactNode }} props
 */
export function PageLayout({ children }) {
  return (
    <>
      <GridBackground />
      <Navbar />
      <main className={styles.main} aria-label="Page content">
        {children}
      </main>
    </>
  )
}
