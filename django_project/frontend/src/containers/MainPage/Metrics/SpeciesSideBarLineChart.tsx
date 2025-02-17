import React, { useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import { Line } from "react-chartjs-2";
import { CategoryScale } from "chart.js";
import Chart from "chart.js/auto";
import axios from "axios";
import Loading from "../../../components/Loading";
import { useAppSelector } from "../../../app/hooks";
import { RootState } from "../../../app/store";
import "./index.scss";

Chart.register(CategoryScale);

const FETCH_PROPERTY_POPULATION_SPECIES = '/api/species-population-count/';

interface PopulationCount {
    year: number;
    year_total: number;
}

interface Species {
    species_name: string;
    annualpopulation_count: PopulationCount[];
}

const speciesColors: { [key: string]: string } = {
    'Lion': '#70B276',
    'Cheetah': '#000000',
    'Elephant': '#A9A9AA',
    'White rhinoceros': '#9F89BF',
    'Black rhinoceros': '#282829',
    'Leopard': '#F9A95D',
    // Add other species and their colors here
};

const SpeciesSideBarLineChart = (props: {property: any}) => {
    const selectedSpecies = ['Lion', 'Cheetah', 'Elephant', 'White rhinoceros', 'Black rhinoceros', 'Leopard'];
    const propertyId = props.property;
    const currentYear = new Date().getFullYear();
    const startYear = currentYear - 1;
    const endYear = currentYear;
    const [loading, setLoading] = useState(false);
    const [speciesData, setSpeciesData] = useState<Species[]>([]);

    const yearsData = Array.from(new Set(speciesData.flatMap(species => species.annualpopulation_count.map(entry => entry.year))));
    yearsData.sort((a, b) => a - b);
    const speciesPopulation = {
        labels: yearsData.map(year => year.toString()),
        datasets: speciesData.map((species) => ({
            label: species.species_name,
            data: yearsData.map(year => {
                const yearData = species.annualpopulation_count.find(entry => entry.year === year);
                return yearData ? yearData.year_total : 0;
            }),
            fill: false,
            borderColor: speciesColors[species.species_name], // Use the color from the mapping
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

    const fetchPropertyPopulation = () => {
        setLoading(true);
        axios.get(`${FETCH_PROPERTY_POPULATION_SPECIES}?start_year=${startYear}&end_year=${endYear}&species=${selectedSpecies}&property=${propertyId}`).then((response) => {
            setLoading(false);
            if (response.data) {
                setSpeciesData(response.data);
            }
        }).catch((error) => {
            setLoading(false);
            console.log(error);
        });
    };

    useEffect(() => {
        fetchPropertyPopulation();
    }, [propertyId]);

    return (
        <Box>
            {!loading ? (
                <Box className="white-chart">
                    <Box className="white-chart-heading">
                        <Typography>Species population counts per year </Typography>
                    </Box>
                    <Line data={speciesPopulation} options={speciesOptions} />
                </Box>) : (
                <Loading />
            )}
        </Box>
    );
};

export default SpeciesSideBarLineChart;
