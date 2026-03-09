import { describe, it, expect } from 'vitest'
import { cn, normalizeStatus, formatFileSize, formatDuration, formatDate, formatShortDate, formatSessionName } from './index'

describe('cn', () => {
  it('joins truthy classes', () => expect(cn('a', 'b')).toBe('a b'))
  it('filters falsy values', () => expect(cn('a', false, null, undefined, 'b')).toBe('a b'))
  it('returns empty string for all falsy', () => expect(cn(false, null)).toBe(''))
})

describe('normalizeStatus', () => {
  it('maps complete to transcribed', () => expect(normalizeStatus('complete')).toBe('transcribed'))
  it('passes through transcribed', () => expect(normalizeStatus('transcribed')).toBe('transcribed'))
  it('passes through processing', () => expect(normalizeStatus('processing')).toBe('processing'))
  it('passes through error', () => expect(normalizeStatus('error')).toBe('error'))
  it('returns unknown statuses as-is', () => expect(normalizeStatus('unknown')).toBe('unknown'))
})

describe('formatShortDate', () => {
  it('formats ISO string to short date', () => {
    const result = formatShortDate('2026-03-08T10:30:00Z')
    expect(result).toMatch(/Mar [78]/)
  })
})

describe('formatFileSize', () => {
  it('formats bytes', () => expect(formatFileSize(512)).toBe('512 B'))
  it('formats kilobytes', () => expect(formatFileSize(1024)).toBe('1 KB'))
  it('formats megabytes', () => expect(formatFileSize(1.5 * 1024 * 1024)).toBe('1.5 MB'))
  it('formats gigabytes', () => expect(formatFileSize(1.8 * 1024 ** 3)).toBe('1.8 GB'))
  it('rounds to 1 decimal', () => expect(formatFileSize(340 * 1024 * 1024)).toBe('340 MB'))
})

describe('formatDuration', () => {
  it('formats minutes only', () => expect(formatDuration(47 * 60)).toBe('47m'))
  it('formats hours and minutes', () => expect(formatDuration(3600 + 23 * 60)).toBe('1h 23m'))
  it('formats zero minutes as 0m', () => expect(formatDuration(0)).toBe('0m'))
  it('formats exactly 1 hour', () => expect(formatDuration(3600)).toBe('1h 0m'))
})

describe('formatDate', () => {
  it('formats ISO string to readable date', () => {
    const result = formatDate('2026-03-07T00:00:00.000Z')
    expect(result).toMatch(/Mar [67], 2026/)
  })
})

describe('formatSessionName', () => {
  it('strips file extension', () =>
    expect(formatSessionName('lecture.mp4')).toBe('Lecture'))
  it('converts underscores to spaces', () =>
    expect(formatSessionName('CS162_Lecture_04.mp4')).toBe('CS162 Lecture 04'))
  it('converts hyphens to spaces', () =>
    expect(formatSessionName('my-class-session.webm')).toBe('My Class Session'))
  it('capitalizes first letter of each word', () =>
    expect(formatSessionName('cs162_lecture_04.mp4')).toBe('Cs162 Lecture 04'))
  it('handles names with no extension', () =>
    expect(formatSessionName('plain name')).toBe('Plain Name'))
})
