import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useEffect, useRef } from 'react'
import { EXPLORE_SPOTS, FAR_AWAY_SPOT_ID } from '../explore'
import type { ExploreSpot } from '../explore'

interface Props {
  spots?: ExploreSpot[]
  activeIndex: number
  onSelect: (index: number) => void
}

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

const pinIcon = (spot: ExploreSpot, index: number, active: boolean) =>
  L.divIcon({
    className: 'map-pin-wrap',
    html: `<span class="map-pin map-pin--${spot.category.replace(/\s/g, '').toLowerCase()}${active ? ' is-active' : ''}"><b>${index + 1}</b></span>`,
    iconSize: [34, 34],
    iconAnchor: [17, 34],
    tooltipAnchor: [0, -34],
  })

/** A map of the campus with a numbered pin for every stop. Clicking a pin opens that stop in the slideshow. */
export default function CampusMap({ spots = EXPLORE_SPOTS, activeIndex, onSelect }: Props) {
  const elementRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<L.Marker[]>([])
  const onSelectRef = useRef(onSelect)
  const startedRef = useRef(false)

  useEffect(() => {
    onSelectRef.current = onSelect
  }, [onSelect])

  // Build the map and its pins once.
  useEffect(() => {
    const element = elementRef.current
    if (!element) return
    const map = L.map(element, { scrollWheelZoom: false, zoomControl: true })
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map)

    markersRef.current = spots.map((spot, i) => {
      const marker = L.marker([spot.lat, spot.lng], { icon: pinIcon(spot, i, false), title: spot.name, keyboard: true })
      marker.bindTooltip(spot.name, { direction: 'top', offset: [0, -2] })
      marker.on('click', () => onSelectRef.current(i))
      return marker.addTo(map)
    })

    const nearby = spots.filter((s) => s.id !== FAR_AWAY_SPOT_ID).map((s) => [s.lat, s.lng] as [number, number])
    map.fitBounds(L.latLngBounds(nearby), { padding: [34, 34] })
    mapRef.current = map
    startedRef.current = false

    return () => {
      map.remove()
      mapRef.current = null
      markersRef.current = []
    }
  }, [spots])

  // Highlight the pin for the current stop, and bring it into view if it is off the map.
  useEffect(() => {
    const map = mapRef.current
    if (!map) return
    markersRef.current.forEach((marker, i) => {
      marker.setIcon(pinIcon(spots[i], i, i === activeIndex))
      marker.setZIndexOffset(i === activeIndex ? 1000 : 0)
    })
    const spot = spots[activeIndex]
    const target = L.latLng(spot.lat, spot.lng)
    // Skip the first run, so the starting view stays the whole campus.
    if (startedRef.current && !map.getBounds().pad(-0.12).contains(target)) {
      const zoom = Math.max(map.getZoom(), 15)
      if (prefersReducedMotion()) map.setView(target, zoom, { animate: false })
      else map.flyTo(target, zoom, { duration: 0.8 })
    }
    startedRef.current = true
  }, [activeIndex, spots])

  const showAll = () => mapRef.current?.fitBounds(L.latLngBounds(spots.map((s) => [s.lat, s.lng] as [number, number])), { padding: [34, 34], animate: !prefersReducedMotion() })
  const showCampus = () =>
    mapRef.current?.fitBounds(L.latLngBounds(spots.filter((s) => s.id !== FAR_AWAY_SPOT_ID).map((s) => [s.lat, s.lng] as [number, number])), { padding: [34, 34], animate: !prefersReducedMotion() })

  return (
    <div className="campus-map">
      <div className="campus-map__head">
        <h2>Campus map</h2>
        <div className="campus-map__views">
          <button type="button" className="link-button" onClick={showCampus}>
            Campus
          </button>
          <button type="button" className="link-button" onClick={showAll}>
            Show all stops
          </button>
        </div>
      </div>
      <div ref={elementRef} className="campus-map__canvas" role="application" aria-label="Map of the Yale campus with a pin for each stop" />
      <p className="campus-map__hint">Tap a pin to jump to that stop. Pin locations are approximate. The Yale Bowl is a few miles west, so use &quot;Show all stops&quot; to see it.</p>
    </div>
  )
}
