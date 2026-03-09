import { NavLink } from 'react-router-dom'
import styles from './Navbar.module.css'

export function Navbar() {
  return (
    <header className={styles.navbar}>
      <div className={styles.inner}>
        <NavLink to="/upload" className={styles.brand} aria-label="Forum Notetaker — go to upload">
          <span className={styles.brandName}>Forum</span>
          <span className={styles.brandSub}>Notetaker</span>
        </NavLink>
        <nav className={styles.nav} aria-label="Main navigation">
          <NavLink
            to="/upload"
            className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}
          >
            Upload
          </NavLink>
          <NavLink
            to="/sessions"
            className={({ isActive }) => isActive ? styles.navLinkActive : styles.navLink}
          >
            Sessions
          </NavLink>
        </nav>
      </div>
    </header>
  )
}
