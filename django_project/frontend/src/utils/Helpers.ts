/**
 * Change string to singular
 */
export function toSingular(str: string) {
    let singularStr = str
    if (str[str.length - 1] === 's') {
      singularStr = singularStr.substring(0, singularStr.length - 1);
    }
    return singularStr
  }
  
  /**
   * Capitalize string
   */
  export function capitalize(str: string) {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }
  
  /**
   * Get file type from layer_type and filename
   */
  export function getFileType(layer_type: string, filename: string): string {
    let extension = filename.split('.').pop()
    let file_type = ''
    if (layer_type === 'GEOJSON')
      file_type = extension==='geojson'?'application/geo+json':'application/json'
    else if (layer_type === 'GEOPACKAGE')
      file_type = 'application/geopackage+sqlite3'
    else if (layer_type === 'SHAPEFILE')
      file_type = 'application/zip'
  
    return file_type
  }
  
  