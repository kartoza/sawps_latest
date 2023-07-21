import React, { useEffect, useState } from "react";
import { Box, FormControl, MenuItem, Select, SelectChangeEvent, Typography } from "@mui/material";
import { Line } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import "./index.scss";
import PropertyInterface from "../../../models/Property";
import axios from "axios";
import Loading from "../../../components/Loading";
import { useAppSelector } from "../../../app/hooks";
import { RootState } from "../../../app/store";

Chart.register(CategoryScale);

const FETCH_PROPERTY_LIST_URL = '/api/property/list/'
const FETCH_PROPERTY_POPULATION_SPECIES = '/species-population-count/'

interface PopulationCount {
    month: number;
    month_total: number;
}

interface Species {
    specie_name: string;
    specie_colour: string;
    annualpopulation_count: PopulationCount[];
}

const SpeciesLineChart = () => {
    const selectedSpecies = useAppSelector((state: RootState) => state.SpeciesFilter.selectedSpecies)
    const selectedMonths = useAppSelector((state: RootState) => state.SpeciesFilter.selectedMonths)
    const startYear = useAppSelector((state: RootState) => state.SpeciesFilter.startYear)
    const endYear = useAppSelector((state: RootState) => state.SpeciesFilter.endYear)
    const [loading, setLoading] = useState(false)
    const [selectedPropertyId, setSelectedPropertyId] = useState<number>(1)
    const [propertyList, setPropertyList] = useState<PropertyInterface[]>([])
    const [speciesData, setSpeciesData] = useState<Species[]>([])
    const speciesPopulation = {
        labels: ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'],
        datasets: speciesData.map((species) => ({
            label: species.specie_name,
            data: species.annualpopulation_count.map((count: PopulationCount) => count.month_total),
            fill: false,
            borderColor: species.specie_colour,
            borderWidth: 1,
        })),
    };

    const speciesOptions = {
        plugins: {
            datalabels: {
                display: false,
            },
            legend: {
                position: 'bottom' as 'bottom',
                labels: {
                    usePointStyle: true,
                    font: {
                        size: 15,
                    },
                    generateLabels: (chart: any) => {
                        const { datasets } = chart.data;
                        return datasets.map((dataset: any, index: any) => ({
                            text: dataset.label,
                            fillStyle: dataset.borderColor,
                            hidden: !chart.isDatasetVisible(index),
                            lineCap: 'round',
                            lineDash: [] as number[],
                            lineDashOffset: 0,
                            lineJoin: 'round',
                            lineWidth: 10,
                            strokeStyle: dataset.borderColor,
                            pointStyle: 'rect',
                            rotation: 0,
                        }))
                    },
                },

            },
        },
        scales: {
            x: {
                beginAtZero: true,
            },
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 65,
                    max: 260,
                },
            },
        },
    };

    const fetchPropertyList = () => {
        setLoading(true)
        axios.get(FETCH_PROPERTY_LIST_URL).then((response) => {
            setLoading(false)
            if (response.data) {
                setPropertyList(response.data as PropertyInterface[])
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }
    const fetchPropertyPopulation = () => {
        setLoading(true)
        axios.get(`${FETCH_PROPERTY_POPULATION_SPECIES}${selectedPropertyId}/?month=${selectedMonths}&start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}`).then((response) => {
            setLoading(false)
            if (response.data) {
                setSpeciesData(response.data)
            }
        }).catch((error) => {
            setLoading(false)
            console.log(error)
        })
    }

    useEffect(() => {
        fetchPropertyList()
    }, [])

    useEffect(() => {
        fetchPropertyPopulation()
    }, [selectedPropertyId, propertyList, selectedMonths, startYear, endYear, selectedSpecies])

    const selectedProperty = propertyList.find((item) => item.id === selectedPropertyId) || propertyList[0];

    return (
        <Box>
            {!loading ? (
                <Box className="white-chart">
                    <Box className="white-chart-heading">
                        <Typography>Species population counts per month for property
                            <span>
                                <FormControl>
                                    <Select
                                        id="property-select"
                                        value={selectedProperty?.name}
                                        className="selecedown"
                                        displayEmpty
                                        disabled={loading}
                                        onChange={(event: SelectChangeEvent) => {
                                            setSelectedPropertyId(parseInt(event.target.value))
                                        }}
                                        renderValue={(selected) => {
                                            if (selected?.length === 0 || selected === '0') {
                                                return <span>{propertyList?.[0].name}</span>
                                            }

                                            return selected
                                        }}
                                    >
                                        {propertyList?.map((property: PropertyInterface) => {
                                            return (
                                                <MenuItem key={property.id} value={property.id}>{property.name}</MenuItem>
                                            )
                                        })}
                                    </Select>
                                </FormControl>
                            </span>
                        </Typography>
                    </Box>
                    <Line data={speciesPopulation} options={speciesOptions} height={450} width={1000} />
                </Box>) : (
                <Loading />
            )
            }
        </Box>
    );
};

export default SpeciesLineChart;
